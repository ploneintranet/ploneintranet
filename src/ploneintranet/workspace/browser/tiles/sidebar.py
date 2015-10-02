# coding=utf-8
from ploneintranet.core import ploneintranetCoreMessageFactory as _  # noqa
from ...basecontent.utils import dexterity_update
from ...interfaces import IGroupingStorage
from ...policies import EXTERNAL_VISIBILITY
from ...policies import JOIN_POLICY
from ...policies import PARTICIPANT_POLICY
from ...utils import map_content_type
from ...utils import parent_workspace
from ...utils import set_cookie
from ...utils import month_name
from ploneintranet.workspace.events import WorkspaceRosterChangedEvent
from AccessControl import Unauthorized
from collective.workspace.interfaces import IWorkspace
from DateTime import DateTime
from plone import api
from plone.app.contenttypes.interfaces import IEvent
from plone.app.event.base import localized_now
from plone.i18n.normalizer import idnormalizer
from ploneintranet.todo.utils import update_task_status
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import getAdapter
from zope.component import getMultiAdapter
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from zope.publisher.browser import BrowserView
import logging

log = logging.getLogger(__name__)


FOLDERISH_TYPES = ['Folder']
BLACKLISTED_TYPES = ['Event', 'todo']


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
            obj=self.context,
        )

    def can_manage_roster(self):
        """
        does this user have permission to manage the workspace's roster
        """
        return api.user.has_permission(
            "ploneintranet.workspace: Manage workspace",
            obj=self.context,
        )

    def can_add(self):
        """
        Is this user allowed to add content?
        Cave. We don't use the plone.app.contenttypes per-type permissions.
        Our workflows don't map those, only cmf.AddPortalContent.
        """
        return api.user.has_permission(
            "Add portal content",
            obj=self.context,
        )

    def can_edit(self):
        """
        Is this user allowed to add content?
        """
        return api.user.has_permission(
            "Modify portal content",
            obj=self.context,
        )

    def can_delete(self, obj=None):
        ''' Is this user allowed to delete an object?
        '''
        if obj is None:
            obj = self.context
        elif hasattr(obj, 'getObject'):
            obj = obj.getObject()
        return api.user.has_permission(
            "Delete objects",
            obj=obj,
        )

    def month_name(self, date):
        """
        Return the full month name in the appropriate language
        """
        return month_name(self, date)


class SidebarSettingsGeneral(BaseTile):

    index = ViewPageTemplateFile('templates/sidebar-settings-general.pt')


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

    def existing_users(self):
        return self.workspace().existing_users()

    def execute_batch_function(self):
        if not self.can_manage_roster():
            msg = _(u'You do not have permission to change the workspace '
                    u'policy')
            raise Unauthorized(msg)

        form = self.request.form
        user_ids = form.get('user_id')
        if not user_ids:
            return

        if isinstance(user_ids, basestring):
            user_ids = user_ids.split(',')

        ws = self.workspace()
        batch_function = form.get('batch-function')
        if batch_function == 'add':
            for user_id in user_ids:
                IWorkspace(ws).add_to_team(user=user_id)
            msg = _(u'Member(s) added')
            msg_type = 'success'
        elif batch_function == 'remove':
            for user_id in user_ids:
                IWorkspace(ws).remove_from_team(user=user_id)
            msg = _(u'Member(s) removed')
            msg_type = 'success'
        elif batch_function == 'role':
            role = self.request.get('role')
            groups = role and {role} or None
            for user_id in user_ids:
                IWorkspace(ws).add_to_team(user=user_id, groups=groups)
            msg = _(u'Role updated')
            msg_type = 'success'
        else:
            msg = _(u'Unknown function')
            msg_type = 'error'

        api.portal.show_message(msg, self.request, msg_type)
        notify(WorkspaceRosterChangedEvent(self.context))

    def __call__(self):
        if self.request.method == 'POST':
            self.execute_batch_function()
        return self.render()


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
            self.form_submitted = True
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
        if self.request.method == 'POST' and form:
            if self.can_manage_workspace():
                modified, errors = dexterity_update(self.context)

                if modified and not errors:
                    api.portal.show_message(
                        _("Attributes changed."),
                        request=self.request,
                        type="success")
                    ws.reindexObject()
                    notify(ObjectModifiedEvent(self.context))

                if errors:
                    api.portal.show_message(
                        _("There was a problem updating the content: %s."
                            % errors),
                        request=self.request,
                        type="error",
                    )

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
            # wft = api.portal.get_tool("portal_workflow")
            section = self.request.form.get('section', None)
            do_reindex = False

            # Do the workflow transitions based on what tasks the user checked
            # or unchecked
            if section == 'task':
                update_task_status(self)

            # Do the property editing. Edits only if there is something to edit
            # in form
            if self.can_manage_workspace() and form:
                modified, errors = dexterity_update(self.context)

                if modified and not errors:
                    api.portal.show_message(
                        _("Attributes changed."),
                        request=self.request,
                        type="success")
                    do_reindex = True
                    notify(ObjectModifiedEvent(self.context))

                if errors:
                    api.portal.show_message(
                        _("There was a problem updating the content: %s."
                            % errors),
                        request=self.request,
                        type="error",
                    )

            if do_reindex:
                ws.reindexObject()
        return self.render()

    def is_open_task_in_milestone(self, milestone_tasks):
        """When viewing a task, open corresponding milestone in sidebar"""
        if 'PARENT_REQUEST' in self.request:
            # Only check if this is a tile subrequest
            open_item_url = self.request.get('PARENT_REQUEST')['ACTUAL_URL']
            return open_item_url in [task['url'] for task in milestone_tasks]
        return False

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

        results = []
        view_types = api.portal.get_registry_record(
            'plone.types_use_view_action_in_listings')
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
                )
                # Do we switch the view (unexpand the sidebar)?
                dps = None
            else:
                # Plone specific:
                # Does it need to be called with a /view postfix?
                if r['portal_type'] in view_types:
                    url = "%s/view" % url
                # What exactly do we need to inject, and where?
                dpi = (
                    "target: #document-body; "
                    "source: #document-body; "
                    "history: record"
                )
                # Do we switch the view (unexpand the sidebar)?
                dps = ("body focus-* focus-document && "
                       "body sidebar-large sidebar-normal")

            results.append(dict(
                title=r['Title'],
                description=r['Description'],
                id=r.getId,
                structural_type=structural_type,
                content_type=content_type,
                dpi=dpi,
                dps=dps,
                url=url,
                creator=api.user.get(username=r['Creator']),
                modified=r['modified'],
                subject=r['Subject'],
                UID=r['UID'],
                path=r.getPath()
            ))
        return results

    def item2ctype(self, item):
        ''' We have an item coming from of one of those two methods:
         - self._extract_attrs
         - self.get_headers_for_group

        We try to return its ctype (content type)
        '''
        ctype = item.get('content_type', 'code')
        if ctype:
            return "type-{0}".format(ctype)
        # we have two fallbacks:
        #  - one for folderish objects
        #  - one for everything else
        if item.get('structural_type') == 'group':
            return 'type-folder'
        return 'document'

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

            ctype = self.item2ctype(item)

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
                username = header['id']
                header['title'] = api.user.get(username=username)\
                    .getProperty('fullname') or username  # admin :-(
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

    def grouping(self):
        """
        Return the user selected grouping
        """
        member = api.user.get_current()
        cookie_name = '%s-grouping-%s' % (self.section, member.getId())
        return self.get_from_request_or_cookie(
            "grouping", cookie_name, "folder")

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

    def events(self):
        """
        Return the events in this workspace
        to be shown in the events section of the sidebar
        """
        catalog = api.portal.get_tool('portal_catalog')
        workspace = parent_workspace(self.context)
        workspace_path = '/'.join(workspace.getPhysicalPath())
        now = localized_now()

        # Current and future events
        upcoming_events = catalog.searchResults(
            object_provides=IEvent.__identifier__,
            path=workspace_path,
            end={'query': now, 'range': 'min'},
            sort_on='start',
            sort_order='ascending',
        )

        # Events which have finished
        older_events = catalog.searchResults(
            object_provides=IEvent.__identifier__,
            path=workspace_path,
            end={'query': now, 'range': 'max'},
            sort_on='start',
            sort_order='descending',
        )
        return {'upcoming': upcoming_events, 'older': older_events}
