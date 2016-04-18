from datetime import datetime
from DateTime import DateTime
from logging import getLogger
from Products.CMFPlone.PloneBatch import Batch
from plone import api
from ploneintranet.search.interfaces import ISearchResponse
from ploneintranet.search.interfaces import ISiteSearch
from ploneintranet.workspace.interfaces import IMetroMap
from zope.component import getUtility
from zope.publisher.browser import BrowserView

logger = getLogger(__name__)


def percent_complete(task_details):
    """Given the data structure used for representing tasks in a case, return a
    string which shows the percentage of completed tasks.
    If a case has no tasks, return an empty string.

    Given:
      task_details = {
        'new': [{'checked': False}],
        'in_progress': [{'checked': True}, {'checked': False}],
      }
    Return:
      '33%'
    """
    tasks = []
    for task_list in task_details.values():
        for task in task_list:
            tasks.append(task)
    if not tasks:
        return ""
    total_task_num = len(tasks)
    complete_tasks = reduce(
        lambda x, y: x + 1 if y["checked"] else x, tasks, 0)
    percentage = int((complete_tasks / float(total_task_num) * 100))
    return "{0}%".format(percentage)


class CaseManagerView(BrowserView):

    def extract_date_field(self, fieldname):
        ''' Extract the date field as a datetime object if possible,
        otherwise return None
        '''
        value = self.request.form.get(fieldname)
        if not value:
            return
        try:
            return datetime.strptime(value, '%Y-%m-%d')
        except ValueError:
            # we suppose we have a date in the wrong format in this case
            return None

    def date_query(self):
        ''' Look for old the possible date parameters and
        return a dict to update the original query
        '''
        date_query = {}
        for date_field in ['created', 'modified']:  # BBB, 'due']:
            earliest = self.extract_date_field('earliest_' + date_field)
            latest = self.extract_date_field('latest_' + date_field)
            if earliest and latest:
                date_query[date_field + '__range'] = (earliest, latest)
            elif earliest:
                date_query[date_field + '__lt'] = earliest
            elif latest:
                date_query[date_field + '__gt'] = latest
        return date_query

    def cases(self):
        pc = api.portal.get_tool('portal_catalog')
        form = self.request.form

        portal = api.portal.get()
        ws_folder = portal.get("workspaces")
        ws_path = "/".join(ws_folder.getPhysicalPath())

        b_size = int(form.get('b_size', 5))
        b_start = int(form.get('b_start', 0))
        sort_by = 'modified'

        query = {
            'portal_type': [
                'ploneintranet.workspace.case'
            ],
            'path': ws_path,
        }

        case_status = form.get('status')

        states = self.get_states()

        if case_status in states:
            query['review_state'] = case_status

        valid_indexes = tuple(pc.indexes())
        for field in valid_indexes:
            if form.get(field):
                query[field] = form.get(field)

        solr_query = self.prepare_solr_query(
            phrase=form.get('SearchableText'),
            query=query
        )

        date_query = self.date_query()
        if date_query:
            solr_query = solr_query.filter(**date_query)

        response = solr_query.execute()
        results = [i for i in ISearchResponse(response)]

        if sort_by == 'modified':
            results.sort(key=lambda item: item.modified, reverse=True)
        else:
            results.sort(key=lambda item: item.title.lower())

        cases = []
        for idx, item in enumerate(results):
            if item is None or idx < b_start or idx > b_start + b_size:
                cases.append(None)
                continue
            path_components = item.path.split('/')
            obj = portal.restrictedTraverse(path_components)
            tasks = obj.tasks()
            days_running = int(DateTime() - DateTime(item.context['created']))
            recent_modifications = len(
                pc(
                    path=item.path,
                    modified={'query': DateTime() - 7, 'range': 'min'},
                )
            )
            cases.append({
                'uid': item.context['UID'],
                'title': item.title,
                'description': item.description,
                'url': item.url,
                'created': item.context['created'],
                'modified': item.context['modified'],
                'mm_seq': IMetroMap(obj).metromap_sequence,
                'tasks': tasks,
                'percent_complete': percent_complete(tasks),
                'recent_modifications': recent_modifications,
                'days_running': days_running,
                'existing_users_by_id': obj.existing_users_by_id(),
                'view': obj.restrictedTraverse('view'),
            })

        return Batch(cases, b_size, b_start)

    def get_field_indexes(self, field):
        catalog = api.portal.get_tool('portal_catalog')
        try:
            indexes = [
                i for i in catalog._catalog.getIndex(field).uniqueValues()
                if i is not None
            ]
        except KeyError:
            logger.warning('Missing index: %s', field)
            indexes = []
        return indexes

    def get_states(self):
        """ Returns only the states known to be in use by cases """
        states = api.portal.get_registry_record(
            'ploneintranet.workspace.case_manager.states'
        )
        return states

    def staff_prefill(self):
        staff = self.request.get('staff')
        if not staff:
            return ''
        user = api.user.get(username=staff)
        if user:
            return u'{{"{0}": "{1} <{2}>"}}'.format(
                staff,
                user.getProperty('fullname') or staff,
                user.getProperty('email'))
        return ''

    def scheduled_session_prefill(self):
        scheduled_session = self.request.get('scheduled_session')
        if not scheduled_session:
            return ''
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog(UID=scheduled_session)
        if len(brains):
            # If len > 1 then all bets are off anyway. Ignoring.
            brain = brains[0]
            return u'{{"{0}": "{1} - {2}"}}'.format(
                scheduled_session,
                brain['start'].strftime('%d.%m.%Y'),
                brain['Title'])
        return ''

    def prepare_solr_query(self, phrase=None, query=None):
        sitesearch = getUtility(ISiteSearch)
        solr_query = sitesearch._create_query_object(phrase)
        solr_query = sitesearch._apply_filters(solr_query, filters=query)
        solr_query = sitesearch._apply_facets(solr_query)
        solr_query = sitesearch._apply_security(solr_query)
        solr_query = sitesearch._paginate(solr_query, start=0, step=9999)
        return solr_query
