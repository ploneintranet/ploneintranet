from datetime import datetime

from AccessControl import Unauthorized
from DateTime import DateTime
from plone import api
from plone.app.contenttypes.interfaces import IEvent
from plone.i18n.normalizer import idnormalizer
from plone.memoize.instance import memoize
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import getAdapter
from zope.component import getMultiAdapter
from zope.publisher.browser import BrowserView

from ... import MessageFactory as _  # noqa
from ...interfaces import IGroupingStorage
from ...policies import EXTERNAL_VISIBILITY
from ...policies import JOIN_POLICY
from ...policies import PARTICIPANT_POLICY
from ...utils import parent_workspace
from ...utils import existing_users
from ...utils import map_content_type
from ...utils import set_cookie
from ploneintranet.todo.behaviors import ITodo

import logging

log = logging.getLogger(__name__)


FOLDERISH_TYPES = ['Folder']
BLACKLISTED_TYPES = ['Event', 'simpletodo']


class BaseTile(BrowserView):

    index = None
    form_submitted = False

    def render(self):
        return self.index()

    def __call__(self):
        return self.render()

    def status_messages(self):
        """
        Returns status messages if any
        """
        messages = IStatusMessage(self.request)
        m = messages.show()
        for item in m:
            item.id = idnormalizer.normalize(item.message)
        return m

    def workspace(self):
        """ Acquire the workspace of the current context
        """
        return parent_workspace(self)

    def can_manage_workspace(self):
        """
        does this user have permission to manage the workspace
        """
        return api.user.has_permission(
            "ploneintranet.workspace: Manage workspace",
            obj=self,
        )


class SidebarSettingsMembers(BaseTile):
    """
    A view to serve as the member roster in the sidebar
    """

    index = ViewPageTemplateFile('templates/sidebar-settings-members.pt')

    def users(self):
        """
        Get current users and add in any search results.

        :returns: a list of dicts with keys
         - id
         - title
        :rtype: list
        """
        existing_users = self.existing_users()
        existing_user_ids = [x['id'] for x in existing_users]

        # Only add search results that are not already members
        sharing = getMultiAdapter((self.workspace(), self.request),
                                  name='sharing')
        search_results = sharing.user_search_results()
        users = existing_users + [x for x in search_results
                                  if x['id'] not in existing_user_ids]

        users.sort(key=lambda x: safe_unicode(x['title']))
        return users

    @memoize
    def existing_users(self):
        return existing_users(self.workspace())


class SidebarSettingsSecurity(BaseTile):
    """
    A view to serve as the security settings in the sidebar
    """

    index = ViewPageTemplateFile('templates/sidebar-settings-security.pt')

    join_policy_label = _(u'join_policy_label', default=u'Join policy')
    external_visibility_label = _(u'external_visibility_label',
                                  default=u'External visibility')
    participant_policy_label = _(u'participant_policy_label',
                                 default=u'Participant policy')

    def __init__(self, context, request):
        """
        Set up local copies of the policies for the sidebar template
        """
        super(SidebarSettingsSecurity, self).__init__(context, request)
        self.external_visibility = EXTERNAL_VISIBILITY
        self.join_policy = JOIN_POLICY
        self.participant_policy = PARTICIPANT_POLICY

    def __call__(self):
        """
        Write attributes, if any, set state, render
        """
        form = self.request.form
        ws = self.workspace()

        def update_field(field_name):
            index = int(form.get(field_name)) - 1
            field = getattr(self, field_name)
            value = field.keys()[index]

            if value != getattr(ws, field_name):
                if field_name == 'external_visibility':
                    ws.set_external_visibility(value)
                else:
                    setattr(ws, field_name, value)
                api.portal.show_message(
                    _(u'Workspace security policy changes saved'),
                    self.request,
                    'success',
                )

        if self.request.method == 'POST':
            if not self.can_manage_workspace():
                msg = _(u'You do not have permission to change the workspace '
                        u'policy')
                raise Unauthorized(msg)
            if form:
                for field in [
                    'external_visibility', 'join_policy', 'participant_policy'
                ]:
                    update_field(field)

        return self.render()


class SidebarSettingsAdvanced(BaseTile):
    """
    A view to serve as the advanced config in the sidebar
    """

    index = ViewPageTemplateFile('templates/sidebar-settings-advanced.pt')

    def __call__(self):
        """ write attributes, if any, set state, render
        """
        form = self.request.form
        ws = self.workspace()

        if self.request.method == 'POST':
            if not self.can_manage_workspace():
                msg = _(u'You do not have permission to change the workspace '
                        u'policy')
                raise Unauthorized(msg)
            if form.get('email') and form.get('email') != ws.email:
                ws.email = form.get('email').strip()
                api.portal.show_message(_(u'Email changed'),
                                        self.request,
                                        'success')
                self.form_submitted = True

        return self.render()


class Sidebar(BaseTile):

    """
    A view to serve as a sidebar navigation for workspaces
    """

    index = ViewPageTemplateFile('templates/sidebar.pt')
    drop_files_label = _(u"drop_files_here",
                         default=u"Drop files here or click to browse...")
    section = "documents"

    def __call__(self):
        """
        Write attributes, if any, set state, render
        """
        form = self.request.form

        if self.request.method == 'POST' and form:
            ws = self.workspace()
            self.set_grouping_cookie()
            if not self.can_manage_workspace():
                msg = _(u'You do not have permission to change the workspace '
                        u'title or description')
                raise Unauthorized(msg)
            if self.request.form.get('section', None) == 'task':
                current_tasks = self.request.form.get('current-tasks', [])
                active_tasks = self.request.form.get('active-tasks', [])

                catalog = api.portal.get_tool('portal_catalog')
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

    def logical_parent(self):
        """
        Needed for the back button in the sidebar.
        Depending on the selected grouping, this returns the information
        needed to get one step back.
        """
        grouping = self.grouping()
        workspace = parent_workspace(self.context)

        if grouping == 'folder':
            if self.context != workspace:
                parent = self.request.PARENTS[1]
                return dict(title=parent.Title(), url=parent.absolute_url())
            else:
                return
        else:
            if self.request.get('groupname'):
                if grouping == 'date':
                    title = _(u'All Dates')
                elif grouping == 'label':
                    title = _(u'All Tags')
                elif grouping == 'author':
                    title = _(u'All Authors')
                elif grouping == 'type':
                    title = _(u'All Types')
                elif grouping == 'first_letter':
                    title = _(u'All Letters')
                else:
                    title = _(u'Back')
                return dict(title=title, url=workspace.absolute_url())
            else:
                return

    def _extract_attrs(self, catalog_results):
        """
        The items to show in the sidebar may come from the current folder or
        a grouping storage for quick access. If they come from the current
        folder, the brains get converted to the same data structure as used
        in the grouping storage to allow unified handling. This extracts the
        attributes from brains and returns dicts
        """
        ptool = api.portal.get_tool('portal_properties')
        results = []
        for r in catalog_results:
            if r['portal_type'] in FOLDERISH_TYPES:
                structural_type = 'group'
            else:
                structural_type = 'item'

            # If it is a file, we have to check the mime type as well
            # And the filename is not enough, we need to guess on the content
            # But that information is not available in the catalog
            # TODO XXX: Add a mime type metadata to the catalog
            content_type = map_content_type(r.mimetype, r.portal_type)

            url = r.getURL()
            if r['portal_type'] in FOLDERISH_TYPES:
                # What exactly do we need to inject, and where?
                dpi = (
                    "source: #workspace-documents; "
                    "target: #workspace-documents "
                    "&& "
                    "source: nav.breadcrumbs; "
                    "target: nav.breadcrumbs; "
                )
            else:
                # Plone specific:
                # Does it need to be called with a /view postfix?
                view_action_types = \
                    ptool.site_properties.typesUseViewActionInListings
                if r['portal_type'] in view_action_types:
                    url = "%s/view" % url
                # What exactly do we need to inject, and where?
                dpi = (
                    "target: #document-body; "
                    "source: #document-body; "
                    "history: record"
                )

            results.append(dict(
                title=r['Title'],
                description=r['Description'],
                id=r.getId,
                structural_type=structural_type,
                content_type=content_type,
                dpi=dpi,
                url=url
            ))
        return results

    def items(self):
        """
        This is called in the template and returns a list of dicts of items in
        the current context.
        It returns the items based on the selected grouping (and later may
        take sorting, archiving etc into account)
        """
        catalog = api.portal.get_tool("portal_catalog")
        current_path = '/'.join(self.context.getPhysicalPath())
        sidebar_search = self.request.get('sidebar-search', None)
        query = {}
        allowed_types = [i for i in api.portal.get_tool('portal_types')
                         if i not in BLACKLISTED_TYPES]
        query['portal_type'] = allowed_types

        #
        # 1. Retrieve the items
        #

        # Depending on the circumstances, this can be
        # * a result of a search,
        # * the top level of a selected grouping
        # * or the items for a selected group item

        if sidebar_search:
            # User has typed a search query

            # XXX plone only allows * as postfix.
            # With solr we might want to do real substr
            query['SearchableText'] = '%s*' % sidebar_search
            query['path'] = current_path
            results = self._extract_attrs(catalog.searchResults(query))

        elif self.request.get('groupname'):
            # User has clicked on a specific group header
            results = self._extract_attrs(self.get_items_in_group())

        else:
            # User has selected a grouping and now gets the headers for that
            results = self.get_headers_for_group()

        #
        # 2. Prepare the results for display in the sidebar
        #

        # Each item must be a dict with at least the following attributes:
        # title, description, id, structural_type, content_type, dpi, url
        # where:
        #   * title, description and id are obvious
        #   * structural_type states if clicking the entry will open it in the
        #     sidebar or in the content area
        #   * content_type is a name for the type usable in css classes.
        #     see utils.TYPE_MAP for a map of plone types to design classes
        #   * dpi is the config that must go into the data-pat-inject attribute
        #     for proper injection
        #   * url is the url that should be called with all params and anchors

        items = []
        for item in results:
            # Do checks to set the right classes for icons and candy

            # Does the item have a description?
            # If so, signal that with a class.
            cls_desc = (
                'has-description' if item.get('description')
                else 'has-no-description'
            )

            ctype = item.get('content_type', 'code')
            if ctype == '':
                ctype = 'document'
            else:
                ctype = "type-{0}".format(ctype)
            cls = 'item %s %s %s' % (
                item.get('structural_type', 'group'), ctype, cls_desc)

            item['cls'] = cls
            item['mime-type'] = ''

            # default to sidebar injection
            if 'dpi' not in item:
                if item.get('structural_type', 'item') == 'group':
                    item['dpi'] = ("source: #workspace-documents; "
                                   "target: #workspace-documents; "
                                   "url: %s" % item['url'])
                else:
                    item['dpi'] = ("source: #document-documents; "
                                   "target: #document-documents; "
                                   "history: record;"
                                   "url: %s" % item['url'])
            items.append(item)

        return items

    def get_items_in_group(self, page_idx=None):
        """
        Return the children for a certain grouping_value
        """
        grouping = self.grouping()
        sorting = self.sorting()
        grouping_value = self.request.get('groupname')
        filter = self.request.get('filter')
        children = self.get_group_children(grouping, grouping_value, filter,
                                           sorting)
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

    def get_headers_for_group(self):
        """
        Return the entries according to a particular grouping
        (e.g. label, author, type, first_letter)
        """
        workspace = parent_workspace(self.context)
        user = api.user.get_current()
        # if the user may not view the workspace, don't bother with
        # getting groups
        if not workspace or not user.has_permission('View', workspace):
            return []

        grouping = self.grouping()
        group_url_tmpl = workspace.absolute_url() + \
            '/@@sidebar.default?groupname=%s#workspace-documents'

        if grouping == 'folder':
            # Group by Folder - use list contents
            query = {}
            allowed_types = [i for i in api.portal.get_tool('portal_types')
                             if i not in BLACKLISTED_TYPES]
            query['portal_type'] = allowed_types
            query['sort_on'] = 'sortable_title'
            return self._extract_attrs(self.context.getFolderContents(query))

        elif grouping == 'date':
            # Group by Date, this is a manual list
            return [dict(title=_(u'Today'),
                         description=_(u'Items modified today'),
                         id='today',
                         structural_type='group',
                         content_type='date',
                         url=group_url_tmpl % 'today'),
                    dict(title=_(u'Last Week'),
                         description=_(u'Items modified last week'),
                         id='week',
                         structural_type='group',
                         content_type='date',
                         url=group_url_tmpl % 'week'),
                    dict(title=_(u'Last Month'),
                         description=_(u'Items modified last month'),
                         id='month',
                         structural_type='group',
                         content_type='date',
                         url=group_url_tmpl % 'month'),
                    dict(title=_(u'All Time'),
                         description=_(u'Items since ever'),
                         id='ever',
                         structural_type='group',
                         content_type='date',
                         url=group_url_tmpl % 'ever')]

        # All other groupings come from the grouping storage,
        # so retrieve that now.
        storage = getAdapter(workspace, IGroupingStorage)

        # In the grouping storage, all entries are accessible under their
        # respective grouping headers. Fetch them for the selected grouping.
        headers = storage.get_order_for(
            grouping,
            include_archived='archived_tags' in self.show_extra,
            alphabetical=True
        )

        if grouping == 'label':
            # Show all labels stored in the grouping storage
            for header in headers:
                header['url'] = group_url_tmpl % header['id']
                header['content_type'] = 'tag'
            # In case of grouping by label, we also must show all
            # unlabeled entries
            headers.append(dict(title='Untagged',
                                description='All items without tags',
                                id='untagged',
                                url=group_url_tmpl % 'Untagged',
                                content_type='tag',
                                archived=False))

        elif grouping == 'author':
            # Show all authors stored in the grouping storage

            # XXX May come soon in UI
            # # If we are grouping by 'author', but the filter is for documents
            # # only by the current user, then we return only the current user
            # # as a grouping.
            # if 'my_documents' in self.show_extra:
            #     username = user.getId()
            #     headers = [dict(title=username,
            #                     description=user.getProperty('fullname'),
            #                     content_type='user',
            #                     url=group_url_tmpl % username,
            #                     id=username)]
            for header in headers:
                header['url'] = group_url_tmpl % header['id']
                header['content_type'] = 'user'

        elif grouping == 'type':
            # Show all types stored in the grouping storage

            # Document types using mimetypes
            headers.append(dict(title='Other',
                                description='Any other document types',
                                id='other'))
            for header in headers:
                content_type = map_content_type(header['id'])
                header['title'] = (content_type and content_type or
                                   header['title']).capitalize()
                header['url'] = group_url_tmpl % header['id']
                header['content_type'] = content_type

        elif grouping == 'first_letter':
            # Show all items by first letter stored in the grouping storage
            for header in headers:
                header['title'] = header['title'].upper()
                header['url'] = group_url_tmpl % header['id']
                header['content_type'] = 'none'

        else:
            # The exception case. Should not happen.
            headers = [dict(title='Ungrouped',
                            description='Other',
                            url=group_url_tmpl % '',
                            content_type='none',
                            id='none')]

        # All headers here are to be displayed as group
        for header in headers:
            header['structural_type'] = 'group'

        return headers

    def get_group_children(self,
                           grouping,
                           grouping_value,
                           filter=None,
                           sorting='modified'):
        """
        Return all the items that have a value $grouping_value for a
        field corresponding to $grouping.
        """
        catalog = api.portal.get_tool(name='portal_catalog')
        workspace = parent_workspace(self.context)
        # workspace_uid = IUUID(workspace)
        criteria = {
            'path': '/'.join(workspace.getPhysicalPath()),
            'fl': 'score Creator Title UID Subject modified outdated '
                  'path_string portal_type getthumb review_state '
                  'sortable_title documentType path_string getIcon '
                  'Description',
            'hl': 'false',
            'sort_on': sorting,
            'sort_order':
            sorting == 'modified' and 'descending' or 'ascending',
        }
        # XXX: This is not yet exposed in the UI, but may soon be
        # if 'my_documents' in self.show_extra:
        #     username = api.user.get_current().getId()
        #     criteria['Creator'] = username

        # if not self.archives_shown():
        #     criteria['outdated'] = False

        def values_in_grouping(name, value):
            gs = IGroupingStorage(workspace)
            groupings = gs.get_groupings()
            grouping = groupings.get(name, dict())
            return [x for x in grouping.get(value, list())]

        documents = []

        if grouping == 'label':
            # This is a bit of an exception compared to the
            # other groupings.
            # We have to check whether grouping_value is 'Untagged', so we
            # query the catalog here and not at the end of the method.
            if grouping_value != 'Untagged':
                criteria['UID'] = values_in_grouping('label', grouping_value)

            brains = catalog(**criteria)
            for brain in brains:
                if grouping_value == 'Untagged' and brain.Subject:
                    continue
                documents.append(brain)

        elif grouping == 'author':
            # XXX This is not yet exposed in the UI, but might be soon.
            # if 'my_documents' in self.show_extra and \
            #         criteria.get('Creator') != grouping_value:
            #     # If the filter is "Documents by me" and the groupingvalue is
            #     # not the current user, we don't return any documents.
            #     return []
            criteria['UID'] = values_in_grouping('author', grouping_value)
            # criteria['Creator'] = grouping_value
            brains = catalog(**criteria)
            for brain in brains:
                documents.append(brain)

        elif grouping == 'date':
            # Show the results grouped by today, the last week,
            # the last month,
            # all time. For every grouping, we exclude the previous one. So,
            # last week won't again include today and all time would exclude
            # the last month.
            today_start = DateTime(DateTime().Date())
            today_end = today_start + 1
            week_start = today_start - 6
            # FIXME: Last month should probably be the last literal month,
            # not the last 30 days.
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

            brains = catalog(**criteria)
            for brain in brains:
                if brain.portal_type == \
                   'ploneintranet.workspace.workspacefolder':
                    continue
                documents.append(brain)

        elif grouping == 'type':
            if grouping_value != 'other':
                criteria['mimetype'] = grouping_value
                brains = catalog(**criteria)
                for brain in brains:
                    if brain.portal_type == \
                       'ploneintranet.workspace.workspacefolder':
                        continue
                    documents.append(brain)
            else:
                brains = catalog(**criteria)
                for brain in brains:
                    if brain.portal_type == \
                       'ploneintranet.workspace.workspacefolder':
                        continue

                    if map_content_type(brain.mimetype):
                        continue
                    documents.append(brain)

        elif grouping == 'first_letter':
            criteria['UID'] = values_in_grouping('first_letter',
                                                 grouping_value)
            brains = catalog(**criteria)
            for brain in brains:
                documents.append(brain)

        return documents

    def set_grouping_cookie(self):
        """
        Set the selected grouping as cookie
        """
        grouping = self.request.get('grouping', 'folder')
        member = api.user.get_current()
        cookie_name = '%s-grouping-%s' % (self.section, member.getId())
        set_cookie(self.request, cookie_name, grouping)

    def get_from_request_or_cookie(self, key, cookie_name, default):
        """
        Helper method to return a value from either request or fallback
        to cookie
        """
        if key in self.request:
            return self.request.get(key)
        if cookie_name in self.request:
            return self.request.get(cookie_name)
        return default

    @memoize
    def grouping(self):
        """
        Return the user selected grouping
        """
        member = api.user.get_current()
        cookie_name = '%s-grouping-%s' % (self.section, member.getId())
        return self.get_from_request_or_cookie(
            "grouping", cookie_name, "folder")

    @memoize
    def sorting(self):
        """
        Return the user selected sorting
        """
        member = api.user.get_current()
        cookie_name = '%s-sort-on-%s' % (self.section, member.getId())
        return self.get_from_request_or_cookie(
            "sorting", cookie_name, "modified")

    @property
    def show_extra(self):
        cookie_name = '%s-show-extra-%s' % (
            self.section, api.user.get_current().getId())
        return self.request.get(cookie_name, '').split('|')

    # def archives_shown(self):
    #     """
    #     Tell if we should show archived items or not
    #     """
    #     return utils.archives_shown(self.context, self.request, self.section)

    # def urlquote(self, value):
    #     """
    #     Encodes values to be used as URL pars
    #     """
    #     return urllib.quote(value)

    @property
    def page_idx(self):
        """
        Helper to return the desired page idx
        """
        return int(self.request.form.get('page_idx', 0))

    @property
    def page_size(self):
        """
        Helper to return the desired page page_size
        """
        return int(self.request.form.get('page_size', 18))

    def tasks(self):
        """
        Show all tasks in the workspace
        """
        items = []
        catalog = api.portal.get_tool('portal_catalog')
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
        """
        Return the events in this workspace
        to be shown in the events section of the sidebar
        """
        catalog = api.portal.get_tool('portal_catalog')
        workspace = parent_workspace(self.context)
        workspace_path = '/'.join(workspace.getPhysicalPath())
        now = datetime.now()

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
        return {'upcoming': upcoming_events, 'older': older_events}
