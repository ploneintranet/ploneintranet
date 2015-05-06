from plone import api
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ploneintranet.workspace import utils
from ploneintranet.workspace.config import SIDEBAR_TYPES
from ploneintranet.workspace.policies import EXTERNAL_VISIBILITY
from ploneintranet.workspace.policies import JOIN_POLICY
from ploneintranet.workspace.policies import PARTICIPANT_POLICY
from zope.publisher.browser import BrowserView
from zope.component import getMultiAdapter
from plone.i18n.normalizer import idnormalizer
from plone.uuid.interfaces import IUUID
from plone.app.contenttypes.interfaces import IEvent
from ploneintranet.workspace import MessageFactory as _
from ploneintranet.workspace.interfaces import IGroupingStorage
from plone.memoize.instance import memoize
from DateTime import DateTime
from Products.CMFPlone.utils import safe_unicode
from Products.CMFCore.utils import _checkPermission as checkPermission
from ploneintranet.todo.behaviors import ITodo
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import getAdapter
from zope.component.interfaces import ComponentLookupError
import urllib
import logging

log = logging.getLogger(__name__)


FOLDERISH_TYPES = ['Folder']
BLACKLISTED_TYPES = ['Event', 'simpletodo']


class BaseTile(BrowserView):

    index = None

    def render(self):
        return self.index()

    def __call__(self):
        return self.render()

    def status_messages(self):
        """ Returns status messages if any
        """
        messages = IStatusMessage(self.request)
        m = messages.show()
        for item in m:
            item.id = idnormalizer.normalize(item.message)
        return m

    def my_workspace(self):
        return utils.parent_workspace(self)


class SidebarSettingsMembers(BaseTile):
    """ A view to serve as the member roster in the sidebar
    """

    index = ViewPageTemplateFile("templates/sidebar-settings-members.pt")

    def users(self):
        """Get current users and add in any search results.

        :returns: a list of dicts with keys
         - id
         - title
        :rtype: list
        """
        existing_users = self.existing_users()
        existing_user_ids = [x['id'] for x in existing_users]

        # Only add search results that are not already members
        sharing = getMultiAdapter((self.my_workspace(), self.request),
                                  name='sharing')
        search_results = sharing.user_search_results()
        users = existing_users + [x for x in search_results
                                  if x['id'] not in existing_user_ids]

        users.sort(key=lambda x: safe_unicode(x["title"]))
        return users

    @memoize
    def existing_users(self):
        return utils.existing_users(self.my_workspace())

    def can_manage_workspace(self):
        """
        does this user have permission to manage the workspace
        """
        return checkPermission(
            "ploneintranet.workspace: Manage workspace",
            self.context,
        )


class SidebarSettingsSecurity(BaseTile):
    """ A view to serve as the security settings in the sidebar
    """

    index = ViewPageTemplateFile("templates/sidebar-settings-security.pt")

    def __init__(self, context, request):
        """ set up local copies of the policies for the sidebar template
        """
        super(SidebarSettingsSecurity, self).__init__(context, request)
        self.external_visibility = EXTERNAL_VISIBILITY
        self.join_policy = JOIN_POLICY
        self.participant_policy = PARTICIPANT_POLICY

    def __call__(self):
        """ write attributes, if any, set state, render
        """
        form = self.request.form

        ws = self.my_workspace()

        def update_field(field_name):
            index = int(form.get(field_name)) - 1
            field = getattr(self, field_name)
            value = field.keys()[index]

            if value != getattr(ws, field_name):
                if field_name == "external_visibility":
                    ws.set_external_visibility(value)
                else:
                    setattr(ws, field_name, value)
                api.portal.show_message(
                    _(u'Workspace security policy changes saved'),
                    self.request,
                    'success',
                )

        if self.request.method == "POST" and form:
            for field in [
                'external_visibility', 'join_policy', 'participant_policy'
            ]:
                update_field(field)

        return self.render()


class SidebarSettingsAdvanced(BaseTile):
    """ A view to serve as the advanced config in the sidebar
    """

    index = ViewPageTemplateFile("templates/sidebar-settings-advanced.pt")

    def __call__(self):
        """ write attributes, if any, set state, render
        """
        form = self.request.form

        if self.request.method == "POST" and form:
            ws = self.my_workspace()

            if form.get('email') and form.get('email') != ws.email:
                ws.email = form.get('email').strip()
                api.portal.show_message(_(u'Email changed'),
                                        self.request,
                                        'success')

        return self.render()


class Sidebar(BaseTile):

    """ A view to serve as a sidebar navigation for workspaces
    """

    index = ViewPageTemplateFile("templates/sidebar.pt")
    section = "documents"

    def __call__(self):
        """ write attributes, if any, set state, render
        """
        form = self.request.form

        if self.request.method == "POST" and form:
            ws = self.my_workspace()
            if self.request.form.get('section', None) == 'task':
                current_tasks = self.request.form.get('current-tasks', [])
                active_tasks = self.request.form.get('active-tasks', [])

                catalog = api.portal.get_tool("portal_catalog")
                brains = catalog(UID={'query': current_tasks,
                                      'operator': 'or'})
                for brain in brains:
                    obj = brain.getObject()
                    todo = ITodo(obj)
                    if brain.UID in active_tasks:
                        todo.status = u'done'
                    else:
                        todo.status = u'tbd'
                api.portal.show_message(_(u'Changes applied'),
                                        self.request,
                                        'success')
            else:
                if form.get('title') and form.get('title') != ws.title:
                    ws.title = form.get('title').strip()
                    api.portal.show_message(_(u'Title changed'),
                                            self.request,
                                            'success')

                if form.get('description') and \
                   form.get('description') != ws.description:
                    ws.description = form.get('description').strip()
                    api.portal.show_message(_(u'Description changed'),
                                            self.request,
                                            'success')

                calendar_visible = not not form.get('calendar_visible')
                if calendar_visible != ws.calendar_visible:
                    ws.calendar_visible = calendar_visible
                    api.portal.show_message(_(u'Calendar visibility changed'),
                                            self.request,
                                            'success')

        return self.render()

    # ContentItems

    def children(self):
        """ returns a list of dicts of items in the current context
        """
        items = []
        catalog = api.portal.get_tool("portal_catalog")
        current_path = '/'.join(self.context.getPhysicalPath())

        sidebar_search = self.request.get('sidebar-search', None)
        query = {}
        allowed_types = [i for i in api.portal.get_tool('portal_types')
                         if i not in BLACKLISTED_TYPES]
        query['portal_type'] = allowed_types
        grouping = self.grouping()

        # 1. Retrieve the children, depending on the circumstances

        if sidebar_search:
            # User has typed a search query
            # XXX plone only allows * as postfix.
            query['SearchableText'] = '%s*' % sidebar_search
            query['path'] = current_path
            # With solr we might want to do real substr
            results = catalog.searchResults(query)
        elif grouping == 'folder':
            # Group by Folder - list contents
            query['sort_on'] = 'sortable_title'
            results = self.context.getFolderContents(query)
        else:
            # Group by other critieria
            results = self.group_headers()

        # 2. Prepare the results for display in the sidebar

        for item in results:
            # Do some checks to set the right classes for icons and candy
            desc = (
                'has-description' if item['Description']
                else 'has-no-description'
            )

            # XXX: will be needed later for grouping by mimetyp
            mime_type = ''
            # typ can be user, folder, date and mime-typish
            portal_type = getattr(item, 'portal_type', '')
            typ = utils.TYPE_MAP.get(portal_type, 'none')
            if hasattr(item, 'getURL'):
                url = item.getURL()
            else:
                url = ''

            ptool = api.portal.get_tool('portal_properties')
            view_action_types = \
                ptool.site_properties.typesUseViewActionInListings

            if portal_type in FOLDERISH_TYPES:
                dpi = (
                    "source: #workspace-documents; "
                    "target: #workspace-documents; "
                    "url: %s/@@sidebar.default#workspace-documents" % url
                )
                content_type = 'group'
            else:
                if portal_type in view_action_types:
                    url = "%s/view" % url
                dpi = (
                    "target: #document-body; "
                    "source: #document-body; "
                    "history: record"
                )
                content_type = 'document'

            cls = 'item %s type-%s %s' % (content_type, typ, desc)

            items.append({
                'id': item['getId'],
                'cls': cls,
                'title': item['Title'],
                'description': item['Description'],
                'url': url,
                'type': typ,
                'mime-type': mime_type,
                'dpi': dpi})
        return items

    def tasks(self):
        items = []
        catalog = api.portal.get_tool("portal_catalog")
        current_path = '/'.join(self.context.getPhysicalPath())
        ptype = 'simpletodo'
        brains = catalog(path=current_path, portal_type=ptype)
        for brain in brains:
            obj = brain.getObject()
            todo = ITodo(obj)
            data = {
                'id': brain.UID,
                'title': brain.Description,
                'content': brain.Title,
                'url': brain.getURL(),
                'checked': todo.status == u'done'
            }
            items.append(data)
        return items

    def events(self):
        catalog = api.portal.get_tool("portal_catalog")
        workspace = utils.parent_workspace(self.context)
        workspace_path = '/'.join(workspace.getPhysicalPath())
        now = DateTime()

        # Current and future events
        upcoming_events = catalog.searchResults(
            object_provides=IEvent.__identifier__,
            path=workspace_path,
            start={'query': (now), 'range': 'min'},
        )

        # Events which have finished
        older_events = catalog.searchResults(
            object_provides=IEvent.__identifier__,
            path=workspace_path,
            end={'query': (now), 'range': 'max'},
        )
        return {"upcoming": upcoming_events, "older": older_events}

    # Grouping code
    def set_show_extra_cookie(self):
        utils.set_show_extra_cookie(self.request, self.section)

    def set_grouping_cookie(self):
        grouping = self.request.get('grouping', 'folder')
        member = api.user.get_current()
        cookie_name = '%s-group-by-%s' % (self.section, member.getId())
        utils.set_cookie(self.request, cookie_name, grouping)

    # def set_sorting_cookie(self):
    #     sorting = self.request.get('sorting', 'modified')
    #     member = api.user.get_current()
    #     cookie_name = '%s-sort-on-%s' % (self.section, member.getId())
    #     utils.set_cookie(self.request, cookie_name, sorting)

    def get_from_request_or_cookie(self, key, cookie_name, default):
        if key in self.request:
            return self.request.get(key)
        if cookie_name in self.request:
            return self.request.get(cookie_name)
        return default

    def grouping(self):
        member = api.user.get_current()
        cookie_name = '%s-grouping-%s' % (self.section, member.getId())
        return self.get_from_request_or_cookie(
            "grouping", cookie_name, "folder")

    # @property
    # def sorting(self):
    #     member = api.user.get_current()
    #     cookie_name = '%s-sort-on-%s' % (self.section, member.getId())
    #     return self.get_from_request_or_cookie(
    #         "sorting", cookie_name, "modified")

    @property
    def show_extra(self):
        cookie_name = '%s-show-extra-%s' % (
            self.section, api.user.get_current().getId())
        return self.request.get(cookie_name, '').split('|')

    def urlquote(self, value):
        """ Encodes values to be used as URL pars
        """
        return urllib.quote(value)

    def group_headers(self):
        """ Return the headers (i.e. values) under a particular grouping
            (e.g. label, author, type).
        """
        workspace = utils.parent_workspace(self.context)
        # if the user may not view the workspace, don't bother with
        # getting groups
        user = api.user.get_current()
        if not user.has_permission('View', workspace):
            return []
        grouping = self.grouping()

        if grouping == 'date':
            return [dict(Title='Today',
                         Description='Items modified today',
                         getId='today'),
                    dict(Title='Last Week',
                         Description='Items modified last week',
                         getId='week'),
                    dict(Title='Last Month',
                         Description='Items modified last month',
                         getId='month'),
                    dict(Title='All Time',
                         Description='Items since ever',
                         getId='ever')]

        try:
            storage = getAdapter(workspace, IGroupingStorage)
        except ComponentLookupError:
            # This happens if objects are loaded outside of an actual workspace
            # which stores the grouping storage. In place just in case
            log.info("Could not load GroupStorage for: %s"
                     % workspace.absolute_url())
            return []

        headers = storage.get_order_for(
            grouping,
            include_archived='archived_tags' in self.show_extra,
            alphabetical=True
        )

        if grouping == 'label':
            headers.append(dict(Title='Untagged',
                                Description='All items without tags',
                                getId='untagged',
                                archived=False))
        elif grouping == 'author':
            # If we are grouping by 'author', but the filter is for documents
            # only by the current user, then we return only the current user as
            # a grouping.
            if 'my_documents' in self.show_extra:
                username = user.getId()
                return [dict(Title=username,
                             Description=user.getProperty('fullname'),
                             getId=username)]
        elif grouping == 'type':
            # Return the human readable titles.
            # vocab = queryUtility(IVocabularyFactory,
            #                      name=config.DOCUMENT_TYPE)(self)
            # headers = [
            #     dict(heading=vocab.getTermByToken(h['heading']).title,
            #          value=vocab.getTermByToken(h['heading']).value)
            #     for h in headers]
            headers = [dict(Title='Meeting Minutes',
                            Description='Minutes and other notes',
                            getId='minutes'),
                       dict(Title='Request Letter',
                            Description='Letters of request',
                            getId='request_letter')]
            headers.append(dict(Title='Other',
                                Description='All other document types',
                                getId='none'))
            return headers
        else:
            return [dict(Title='Ungrouped',
                         Description='Other',
                         getId='none')]
        return headers

    def get_items_by(self,
                     grouping,
                     grouping_value,
                     filter=None,
                     sorting='modified'):
        """ Return all the documents that have a value $grouping_value for a
            field corresponding to $grouping.
        """
        # Somehow we missed adding the documentType index to the ZCatalog. It's
        # there now, but as long as it's not filled with enough values we use
        # solr instead for grouping by type
        if grouping == 'type':
            catalog = api.portal.get_tool(name='portal_catalog')
        else:
            catalog = api.portal.get_tool(name='portal_catalog')\
                ._cs_old_searchResults

        # XXX Try doing solr only as we are injecting items via JS anyway,
        # a delay doesn't matter

        workspace = utils.get_workspace_or_contract(self.context)
        context_uid = IUUID(workspace)
        criteria = {
            'path': '/'.join(workspace.getPhysicalPath()),
            'fl': 'score Creator Title UID Subject modified outdated '
                  'path_string portal_type getthumb review_state '
                  'sortable_title documentType path_string getIcon '
                  'Description',
            'hl': 'false',
            'portal_type': SIDEBAR_TYPES,
            'sort_on': sorting,
            'sort_order':
            sorting == 'modified' and 'descending' or 'ascending',
        }
        if 'my_documents' in self.show_extra:
            username = api.user.get_current().getId()
            criteria['Creator'] = username

        if not self.archives_shown():
            criteria['outdated'] = False

        documents = []
        if grouping in ('label', 'label_custom'):
            # This is a bit of an exception compared to the other 3 groupings.
            # We have to check whether grouping_value is 'Untagged', so we
            # query the catalog here and not at the end of the method.
            if grouping_value != 'Untagged':
                gs = IGroupingStorage(workspace)
                groupings = gs.get_groupings()
                by_label = groupings.get('label', dict())
                criteria['UID'] = [
                    x for x in by_label.get(grouping_value, list())]
                del criteria['path']

            brains = catalog(**criteria)
            for brain in brains:
                if brain is None or brain.UID == context_uid:
                    continue
                if grouping_value == 'Untagged' and brain.Subject:
                    continue
                documents.append(self.make_leaf(brain))
            return documents

        if grouping == 'author':
            if 'my_documents' in self.show_extra and \
                    criteria.get('Creator') != grouping_value:
                # If the filter is "Documents by me" and the grouping_value is
                # not the current user, we don't return any documents.
                return []
            criteria['Creator'] = grouping_value

        elif grouping == 'period':
            # Show the results grouped by today, the last week, the last month,
            # all time. For every grouping, we exclude the previous one. So,
            # last week won't again include today and "all time" would exclude
            # the last month.
            today_start = DateTime(DateTime().Date())
            today_end = today_start + 1
            week_start = today_start - 6
            # FIXME: Last month should probably be the last literal month, not
            # the last 30 days.
            month_start = today_start - 30

            if grouping_value == 'Today':
                criteria['modified'] = \
                    {'range': 'min:max', 'query': (today_start, today_end)}
            elif grouping_value == 'Last Week':
                criteria['modified'] = \
                    {'range': 'min:max', 'query': (week_start, today_start)}
            elif grouping_value == 'Last Month':
                criteria['modified'] = \
                    {'range': 'min:max', 'query': (month_start, week_start)}
            elif grouping_value == 'All Time':
                criteria['modified'] = {'range': 'max', 'query': month_start}

        elif grouping == 'type':
            if grouping_value != 'none':
                criteria['documentType'] = grouping_value
            else:
                brains = catalog(**criteria)
                for brain in brains:
                    if brain is None or brain.UID == context_uid:
                        continue
                    if brain.documentType:
                        continue
                    documents.append(self.make_leaf(brain))
                return documents

        brains = catalog(**criteria)
        for brain in brains:
            if brain is None or brain.UID == context_uid:
                continue
            documents.append(self.make_leaf(brain))

        return documents

    # @view.memoize
    def get_children(self, page_idx=None):
        """ Return the children for a certain grouping_value
        """
        grouping = self.request.get('grouping', None)
        sorting = self.request.get('sorting', 'modified')
        grouping_value = self.request.get('groupname', '')
        filter = self.request.get('filter')
        children = self.get_items_by(grouping, grouping_value, filter, sorting)
        if page_idx is None:
            page_idx = self.page_idx
        page_size = self.page_size
        if page_size < 0:
            return children
        try:
            batch = children[page_idx * page_size:(page_idx + 1) * page_size]
        except IndexError:
            batch = children[page_idx * page_size:]
        return batch
