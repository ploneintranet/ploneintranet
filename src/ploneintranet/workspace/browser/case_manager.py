from DateTime import DateTime
from Products.CMFPlone.PloneBatch import Batch
from plone import api
from ploneintranet.search.interfaces import ISiteSearch
from ploneintranet.workspace.config import TRANSITION_ICONS
from ploneintranet.workspace.interfaces import IMetroMap
from zope.component import getUtility
from zope.publisher.browser import BrowserView
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


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

    transition_icons = TRANSITION_ICONS

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
            'portal_type': 'ploneintranet.workspace.case',
            'path': ws_path,
        }

        for date in ['created', 'modified', 'due']:
            if form.get('earliest_' + date) and form.get('latest_' + date):
                query[date] = {
                    'query': (
                        DateTime(form.get('earliest_' + date)),
                        DateTime(form.get('latest_' + date))
                    ),
                    'range': 'min:max',
                }
            elif form.get('earliest_' + date):
                query[date] = {
                    'query': DateTime(form.get('earliest_' + date)),
                    'range': 'min',
                }
            elif form.get('latest_' + date):
                query[date] = {
                    'query': DateTime(form.get('latest_' + date)),
                    'range': 'max',
                }

        case_status = form.get('status')
        if case_status:
            if case_status == "open":
                query['review_state'] = [
                    'complete', 'decided', 'in_progress', 'new', 'request']
            elif case_status == "closed":
                query['review_state'] = ['archived', 'closed', 'rejected']
        valid_indexes = tuple(pc.indexes())
        for field in valid_indexes:
            if form.get(field):
                query[field] = form.get(field)

        sitesearch = getUtility(ISiteSearch)

        if 'SearchableText' in form:
            response = list(
                sitesearch.query(
                    phrase=form['SearchableText'], filters=query, step=99999)
            )
        else:
            response = list(sitesearch.query(filters=query, step=99999))

        if sort_by == 'modified':
            response.sort(key=lambda item: item.modified, reverse=True)
        else:
            response.sort(key=lambda item: item.title.lower())

        cases = []
        for idx, item in enumerate(response):
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
        indexes = [
            i for i in catalog._catalog.getIndex(field).uniqueValues()
            if i is not None
        ]
        return indexes

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

    def case_types(self):
        case_types = \
            api.portal.get_registry_record('ikath.intranet.case_types')
        terms = [SimpleTerm(value=ct, token=ct, title=case_types[ct])
                 for ct in case_types]
        terms.sort(cmp=lambda x, y: cmp(x.title, y.title))
        return SimpleVocabulary(terms)
