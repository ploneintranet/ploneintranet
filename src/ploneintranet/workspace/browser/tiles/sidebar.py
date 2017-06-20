# coding=utf-8
from ...basecontent.utils import dexterity_update
from ...interfaces import IGroupingStorage
from ...policies import EXTERNAL_VISIBILITY
from ...policies import JOIN_POLICY
from ...policies import PARTICIPANT_POLICY
from ...utils import map_content_type
from ...utils import parent_workspace
from ...utils import set_cookie
from .events import format_event_date_for_title
from AccessControl import Unauthorized
from collective.workspace.interfaces import IWorkspace
from DateTime import DateTime
from itertools import ifilter
from plone import api
from plone.app.contenttypes.interfaces import IEvent
from plone.app.event.base import localized_now
from plone.behavior.interfaces import IBehaviorAssignable
from plone.i18n.normalizer import idnormalizer
from plone.memoize.view import memoize
from plone.memoize.view import memoize_contextless
from plone.protect.authenticator import createToken
from ploneintranet import api as pi_api
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.layout.utils import get_record_from_registry
from ploneintranet.layout.utils import shorten
from ploneintranet.search.interfaces import ISiteSearch
from ploneintranet.todo.utils import update_task_status
from ploneintranet.workspace.browser.show_extra import set_show_extra_cookie
from ploneintranet.workspace.events import WorkspaceRosterChangedEvent
from Products.Archetypes.utils import shasattr
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from slc.mailrouter.utils import store_name
from urllib import quote
from urllib import urlencode
from zope.component import getAdapter
from zope.component import getUtility
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from zope.publisher.browser import BrowserView
from zope.schema import getFieldNames
from zope.schema.interfaces import IVocabularyFactory

import logging


log = logging.getLogger(__name__)

vocab = 'ploneintranet.workspace.vocabularies.Divisions'


class BaseTile(BrowserView):

    """
    Shared baseclass for the sidebar tiles.

    Cave: many of the actual sidebar templates *also* bind to
    ploneintranet.workspace.browser.workspace.WorkspaceView
    to use methods defined there...
    """

    index = None
    form_submitted = False

    general_settings_autoload = 'trigger: autoload;'

    @property
    @memoize
    def current_user(self):
        ''' Return the current authenticated user id
        '''
        return api.user.get_current()

    @property
    @memoize
    def current_userid(self):
        ''' Return the current authenticated user id
        '''
        return self.current_user.getId()

    def render(self):
        return self.index()

    def __call__(self):
        return self.render()

    def _basic_save(self):
        ''' Performs a simple save of entered attributes.
            Not all sidebars need this
        '''
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
                    if form.get('hero_image', None):
                        self.request.response.redirect(
                            self.context.absolute_url())

                if errors:
                    api.portal.show_message(
                        _("There was a problem updating the content: %s."
                            % errors),
                        request=self.request,
                        type="error",
                    )

    def status_messages(self):
        """
        Returns status messages if any
        """
        messages = IStatusMessage(self.request)
        m = messages.show()
        for item in m:
            item.id = idnormalizer.normalize(item.message)
        return m

    @memoize
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
        if shasattr(self.context, 'disable_add_from_sidebar'):
            if self.context.disable_add_from_sidebar:
                return False

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

    def can_subscribe(self):
        ''' Check if we see the subscribe feature in the bulk actions
        '''
        return get_record_from_registry(
            'ploneintranet.workspace.allow_bulk_subscribe', False
        )

    def date_as_datetime(self, date):
        '''
            The content items in the sidebar have a `DateTime` as their
            modification date. But search results have a `datetime`.
        '''
        if isinstance(date, DateTime):
            date = date.asdatetime()
        return date


class SidebarSettingsGeneral(BaseTile):

    index = ViewPageTemplateFile('templates/sidebar-settings-general.pt')

    def __call__(self):
        """ write attributes, if any, set state, render
        """
        self._basic_save()
        return self.render()


class SidebarSettingsMembers(BaseTile):

    """
    A view to serve as the member roster in the sidebar
    """

    index = ViewPageTemplateFile('templates/sidebar-settings-members.pt')

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

    def get_avatar_by_userid(self, userid):
        ''' Provide HTML tag to display the avatar
        '''
        return pi_api.userprofile.avatar_tag(
            username=userid,
        )

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
                try:
                    if field_name == 'external_visibility':
                        ws.set_external_visibility(value)
                    else:
                        setattr(ws, field_name, value)
                    msg = _(u'Workspace security policy changes saved')
                    msg_type = 'success'
                except:
                    msg = _(u'Workspace security policy change failed')
                    log.exception('Workspace security policy change failed')
                    msg_type = 'error'
                api.portal.show_message(
                    msg,
                    self.request,
                    msg_type,
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

    def can_delete_workspace(self):
        ws = parent_workspace(self.context)
        return api.user.has_permission(
            "Delete objects",
            obj=ws,
        )

    def can_be_division(self):
        ''' Check if this object can be a division,
        i.e. has a division field in the schema or in a behavior
        '''
        schema = self.context.getTypeInfo().lookupSchema()
        if 'is_division' in getFieldNames(schema):
            return True

        behavior_assignable = IBehaviorAssignable(self.context)
        if behavior_assignable:
            behaviors = behavior_assignable.enumerateBehaviors()
            for behavior in behaviors:
                if 'is_division' in getFieldNames(schema):
                    return True
        return False

    def update_relation_targets(self, old_relations):
        ''' Get old relations and new relations and update the targets
        to point to self.context.
        '''
        context_uid = self.context.UID()
        old_relations = set(old_relations or [])
        new_relations = set(self.context.related_workspaces or [])
        to_add = new_relations - old_relations
        for uid in to_add:
            target = api.content.get(UID=uid)
            if target:
                if not target.related_workspaces:
                    target.related_workspaces = [context_uid]
                elif context_uid not in target.related_workspaces:
                    target.related_workspaces.append(context_uid)

        to_remove = old_relations - new_relations
        for uid in to_remove:
            target = api.content.get(UID=uid)
            if (
                target and
                target.related_workspaces and
                context_uid in target.related_workspaces
            ):
                target.related_workspaces.remove(context_uid)

    def __call__(self):
        """ write attributes, if any, set state, render
        """
        form = self.request.form
        if self.request.method == 'POST' and form:
            if self.can_manage_workspace():
                if 'email' in form and form['email']:
                    if '@' in form['email']:
                        # Only use the name part as the domain is fixed.
                        form['email'] = form['email'].split('@')[0]
                if 'related_workspaces' in form and form['related_workspaces']:
                    # We defined this as a list of TextLine values.
                    # Therefore, the value from the form must be passed
                    # as a string with one value per line.
                    value = form['related_workspaces']
                    # First, if this is a list, flatten to a comma-separated
                    # string
                    value = ','.join([x for x in value if x])
                    # Now, replace all commas with a new-line character
                    value = value.replace(',', '\n')
                    form['related_workspaces'] = value
                    old_related_workspaces = self.context.related_workspaces
                else:
                    old_related_workspaces = ''

                modified, errors = dexterity_update(self.context)

                self.update_relation_targets(old_related_workspaces)

                if 'email' in form and form['email']:
                    errors += store_name(self.context, form['email']).values()

                if modified and not errors:
                    api.portal.show_message(
                        _("Attributes changed."),
                        request=self.request,
                        type="success")
                    notify(ObjectModifiedEvent(self.context))

                if errors:
                    api.portal.show_message(
                        _("There was a problem updating the content: %s."
                            % errors),
                        request=self.request,
                        type="error",
                    )

        return self.render()

    def divisions(self):
        """ return available divisions """
        divisions = getUtility(IVocabularyFactory, vocab)(self.context)
        return divisions


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
            section = self.request.form.get('section', self.section)
            set_show_extra_cookie(self.request, section)
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
        workspace = self.root

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
                elif grouping.startswith('label'):
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
        folderish_types = self.folderish_types
        for r in catalog_results:
            # If it is a file, we have to check the mime type as well
            # And the filename is not enough, we need to guess on the content
            # But that information is not available in the catalog
            # TODO XXX: Add a mime type metadata to the catalog
            content_type = map_content_type(r.mimetype, r.portal_type)

            url = r.getURL()
            if r['portal_type'] in folderish_types:
                structural_type = 'group'
                # What exactly do we need to inject, and where?
                dpi = (
                    "source: #workspace-documents; "
                    "target: #workspace-documents "
                )
                # Do we switch the view (unexpand the sidebar)?
                dps = None
                url = "%s/@@sidebar.documents" % url
            else:
                structural_type = 'document'
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
                dps = ("#application-body focus-* focus-document && "
                       "#application-body sidebar-large sidebar-normal")

            results.append(dict(
                title=r['Title'],
                description=r['Description'],
                id=r['getId'],
                structural_type=structural_type,
                content_type=content_type,
                dpi=dpi,
                dps=dps,
                url=url,
                creator=r['Creator'],
                modified=r['modified'],
                subject=r['Subject'],
                UID=r['UID'],
                path=r.getPath(),
                outdated=r['outdated'],
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

    def update_with_show_extra(self, query):
        ''' Update the query with the values from show_extra cookie
        '''
        show_extra = self.show_extra
        if 'my_documents' in show_extra:
            query['Creator'] = self.current_userid
        if 'archived_documents' not in show_extra:
            query['outdated'] = False

    @property
    @memoize
    def root(self):
        """ The root object for the sidebar, typically a workspace, but the
        sidebar can also be used for apps, e.g. quaive.app.slides.
        """
        return parent_workspace(self.context)

    @property
    @memoize_contextless
    def folderish_types(self):
        ''' The portal_types considered as foldersish for the sidebar
        The email type, e.g., is folderish but is threated by the UI
        as a non folderish one.
        '''
        portal_types = get_record_from_registry(
            'ploneintranet.workspace.sidebar.folderish_types',
            ('Folder',)
        )
        return portal_types

    @property
    @memoize_contextless
    def blacklisted_item_types(self):
        ''' The portal_types that will not be included in the document sidebar
        because they have their own sidebar
        '''
        portal_types = get_record_from_registry(
            'ploneintranet.workspace.sidebar.blacklisted_types',
            ('Event', 'todo', )
        )
        if self.grouping() != u'folder':
            portal_types += self.folderish_types
        return portal_types

    @property
    @memoize_contextless
    def portal_types_filter(self):
        ''' Some contents are threated differently, e.g. todo and events
        We want to include folderish types only if we are grouping by folder
        '''
        all_types = set(api.portal.get_tool('portal_types'))
        all_types.difference_update(self.blacklisted_item_types)
        return list(all_types)

    def result2item(self, result):
        ''' Make a result out of an item
        '''
        # BBB: For the time being item is a dictionary that contains everything
        # this should change
        item = result

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
        # Work around a solr-quirk: We might end up with "/view" being
        # appended twice to the URL. See #1056
        if item['url'].endswith('/view/view'):
            item['url'] = item['url'][:-5]

        # default to sidebar injection
        if 'dpi' in item:
            return item

        if item.get('structural_type', 'item') == 'group':
            item['dpi'] = ("source: #workspace-documents; "
                           "target: #workspace-documents; "
                           "url: %s" % item['url'])
        else:
            item['dpi'] = ("source: #document-documents; "
                           "target: #document-documents; "
                           "history: record;"
                           "url: %s" % item['url'])
        return item

    def items(self):
        """
        This is called in the template and returns a list of dicts of items in
        the current context.
        It returns the items based on the selected grouping (and later may
        take sorting, archiving etc into account)
        """
        current_path = '/'.join(self.context.getPhysicalPath())
        sidebar_search = self.request.get('sidebar-search', None)
        query = {}
        query['portal_type'] = self.portal_types_filter
        self.update_with_show_extra(query)

        #
        # 1. Retrieve the items
        #

        # Depending on the circumstances, this can be
        # * a result of a search,
        # * the top level of a selected grouping
        # * or the items for a selected group item

        root = self.root
        if sidebar_search:
            # User has typed a search query

            sitesearch = getUtility(ISiteSearch)
            query['path'] = current_path
            # XXX plone only allows * as postfix.
            # With solr we might want to do real substr
            response = sitesearch.query(phrase='%s*' % sidebar_search,
                                        filters=query,
                                        step=99999,
                                        restricted_filters=False)
            results = self._extract_attrs(response)

        elif self.request.get('groupname'):
            # User has clicked on a specific group header
            results = self._extract_attrs(self.get_items_in_group())

        else:
            # User has selected a grouping and now gets the headers for that
            results = self.get_headers_for_group()

        root_uid = root.UID()
        results = ifilter(
            lambda result: result.get('UID') != root_uid,
            results
        )

        #
        # 2. Prepare the results for display in the sidebar
        # Make sure we first show the group-elements (= folders or similar)
        # before any content items
        # Note: since False==0, it gets sorted before True!
        #

        if self.grouping() not in ['date', 'label_custom']:
            results = sorted(results, key=lambda x: (
                x['structural_type'] != 'group', x['title'].lower()))

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
        return map(self.result2item, results)

    def get_items_in_group(self):
        """
        Return the children for a certain grouping_value
        """
        grouping = self.grouping()
        sorting = self.sorting()
        grouping_value = self.request.get('groupname')
        children = self.get_group_children(grouping, grouping_value, sorting)
        return children

    def group_url(self, groupname):
        ''' Return the url for this group
        '''
        return (
            '{context_url}/@@sidebar.documents?'
            'groupname={groupname}#workspace-documents'
        ).format(
            context_url=self.root.absolute_url(),
            groupname=quote(groupname),
        )

    def get_headers_for_group(self):
        """
        Return the entries according to a particular grouping
        (e.g. label, author, type, first_letter)
        """
        root = self.root
        # if the user may not view the workspace, don't bother with
        # getting groups
        user = self.current_user
        if not root or not user.has_permission('View', root):
            return []

        grouping = self.grouping()

        if grouping == 'folder':
            # Group by Folder - use list contents
            query = {
                'sort_on': 'sortable_title',
                'path': {
                    'query': '/'.join(self.context.getPhysicalPath()),
                    'depth': 1,
                },
                'portal_type': self.portal_types_filter,
            }
            return self._extract_attrs(self.query_items(query))

        if grouping == 'date':
            # Group by Date, this is a manual list
            return [dict(title=_(u'Today'),
                         description=_(u'Items modified today'),
                         id='today',
                         structural_type='group',
                         content_type='date',
                         url=self.group_url('today')),
                    dict(title=_(u'Last Week'),
                         description=_(u'Items modified last week'),
                         id='week',
                         structural_type='group',
                         content_type='date',
                         url=self.group_url('week')),
                    dict(title=_(u'Last Month'),
                         description=_(u'Items modified last month'),
                         id='month',
                         structural_type='group',
                         content_type='date',
                         url=self.group_url('month')),
                    dict(title=_(u'All Time'),
                         description=_(u'Older'),
                         id='ever',
                         structural_type='group',
                         content_type='date',
                         url=self.group_url('ever')),
                    ]

        # All other groupings come from the grouping storage,
        # so retrieve that now.
        storage = getAdapter(root, IGroupingStorage)

        # In the grouping storage, all entries are accessible under their
        # respective grouping headers. Fetch them for the selected grouping.
        if grouping.startswith('label'):
            include_archived = self.archived_tags_shown()
        else:
            include_archived = self.archived_documents_shown()

        if grouping.startswith('label'):
            # Show all labels stored in the grouping storage
            headers = storage.get_order_for(
                'label',
                include_archived=include_archived,
                alphabetical=False
            )
            for header in headers:
                header['url'] = self.group_url(header['id'])
                header['content_type'] = 'tag'
            # In case of grouping by label, we also must show all
            # unlabeled entries
            headers.append(dict(title='Untagged',
                                description='All items without tags',
                                id='untagged',
                                url=self.group_url('Untagged'),
                                content_type='tag',
                                archived=False))

        elif grouping == 'author':
            headers = storage.get_order_for(
                grouping,
                include_archived=include_archived,
                alphabetical=True
            )
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
            workspace_view = api.content.get_view(
                'view',
                root,
                self.request,
            )
            for header in headers:
                userid = header['id']
                header['title'] = workspace_view.get_principal_title(userid)
                header['url'] = self.group_url(header['id'])
                header['content_type'] = 'user'

        elif grouping == 'type':
            # Show all types stored in the grouping storage
            headers = storage.get_order_for(
                grouping,
                include_archived=include_archived,
                alphabetical=True
            )

            # Document types using mimetypes
            headers.append(dict(title='Other',
                                description='Any other document types',
                                id='other'))
            for header in headers:
                content_type = map_content_type(header['id'])
                header['title'] = (content_type and content_type or
                                   header['title']).capitalize()
                header['url'] = self.group_url(header['id'])
                header['content_type'] = content_type

        elif grouping == 'first_letter':
            # Show all items by first letter stored in the grouping storage
            headers = storage.get_order_for(
                grouping,
                include_archived=include_archived,
                alphabetical=True
            )
            for header in headers:
                header['title'] = header['title'].upper()
                header['url'] = self.group_url(header['id'])
                header['content_type'] = 'none'

        else:
            # The exception case. Should not happen.
            headers = [dict(title='Ungrouped',
                            description='Other',
                            url=self.group_url(''),
                            content_type='none',
                            id='none')]

        # All headers here are to be displayed as group
        for header in headers:
            header['structural_type'] = 'group'

        return headers

    def get_groupings(self):
        ''' Return the whole grouping storage
        '''
        gs = IGroupingStorage(self.root)
        groupings = gs.get_groupings()
        return groupings

    def get_grouping_by_name(self, name=None):
        ''' Get the grouping from the grouping storage given a name
        If no name is given default to the one returned by self.get_groupings()
        '''
        if name is None:
            name = self.groupings()
        groupings = self.get_groupings()
        grouping = groupings.get(name, {})
        return grouping

    def uids_in_grouping(self, name, value):
        ''' Get the values in grouping

        name is something like: 'label', 'author', ...
        value is something like 'tag1', 'john.doe', ...
        '''
        grouping = self.get_grouping_by_name(name)
        return list(grouping.get(value, []))

    def get_base_query(self):
        ''' This is the base query for searching inside a workspace
        '''
        sorting = self.sorting()
        sort_order = sorting == 'modified' and 'descending' or 'ascending'
        query = {
            'path': '/'.join(self.root.getPhysicalPath()),
            'sort_on': sorting,
            'sort_order': sort_order,
            'portal_type': self.portal_types_filter
        }
        show_extra = self.show_extra
        if 'my_documents' in show_extra:
            query['Creator'] = self.current_userid
        if 'archived_documents' not in show_extra:
            query['outdated'] = False
        return query

    def query_items(self, additional_query={}):
        ''' Return all the documents in the group for the given query
        '''
        query = self.get_base_query()
        query.update(additional_query)
        catalog = api.portal.get_tool(name='portal_catalog')
        return catalog(**query)

    def get_group_children_by_label(
        self,
        grouping,
        grouping_value,
        sorting='modified'
    ):
        ''' Get the children from the given label
        '''
        if grouping_value != 'Untagged':
            uids = self.uids_in_grouping('label', grouping_value)
            if not uids:
                return []
            return self.query_items({'UID': uids})

        def is_untagged(doc):
            ''' BBB: This is a temporary compatibility method to make this
            function work with brains and ISiteSearch results.
            For a brain we want to get the Subject attribute,
            for an ISiteSearch result, Subject is a method.
            '''
            subject = doc.Subject
            if callable(subject):
                subject = subject()
            return not(subject)

        return filter(is_untagged, self.query_items())

    def get_group_children_by_date(
        self,
        grouping,
        grouping_value,
        sorting='modified'
    ):
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

        if grouping_value == 'today':
            modified = {
                'range': 'min:max',
                'query': (today_start, today_end),
            }
        elif grouping_value == 'week':
            modified = {
                'range': 'min:max',
                'query': (week_start, today_start)
            }
        elif grouping_value == 'month':
            modified = {
                'range': 'min:max',
                'query': (month_start, week_start)
            }
        elif grouping_value == 'ever':
            modified = {
                'range': 'max',
                'query': month_start
            }
        else:
            modified = ''
        return self.query_items({'modified': modified})

    def get_group_children_by_type(
        self,
        grouping,
        grouping_value,
        sorting='modified'
    ):
        if grouping_value != 'other':
            uids = self.uids_in_grouping(grouping, grouping_value)
            if not uids:
                return []
            return self.query_items({'UID': uids})
        brains = self.query_items()
        return [
            brain for brain in brains
            if not map_content_type(brain.mimetype)
        ]

    def get_group_children(self,
                           grouping,
                           grouping_value,
                           sorting='modified'):
        """
        Return all the items that have a value $grouping_value for a
        field corresponding to $grouping.
        """
        if grouping.startswith('label'):
            return self.get_group_children_by_label(
                grouping,
                grouping_value,
                sorting,
            )

        if grouping == 'date':
            return self.get_group_children_by_date(
                grouping,
                grouping_value,
                sorting,
            )

        if grouping == 'type':
            return self.get_group_children_by_type(
                grouping,
                grouping_value,
                sorting,
            )

        # When no fancy things are needed, this should be enough
        uids = self.uids_in_grouping(grouping, grouping_value)
        if not uids:
            return []
        return self.query_items({'UID': uids})

    def set_grouping_cookie(self):
        """
        Set the selected grouping as cookie
        """
        grouping = self.request.get('grouping', 'folder')
        cookie_name = '%s-grouping-%s' % (self.section, self.current_userid)
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
    def get_default_grouping(self):
        ''' Get the default grouping for document navigation in the sidebar
        '''
        return get_record_from_registry(
            'ploneintranet.workspace.default_grouping',
            'folder',
        )

    def grouping(self):
        """
        Return the user selected grouping
        """
        cookie_name = '%s-grouping-%s' % (self.section, self.current_userid)
        return self.get_from_request_or_cookie(
            "grouping", cookie_name, self.get_default_grouping(),
        )

    def sorting(self):
        """
        Return the user selected sorting
        """
        cookie_name = '%s-sort-on-%s' % (self.section, self.current_userid)
        return self.get_from_request_or_cookie(
            "sorting", cookie_name, "modified")

    @property
    @memoize
    def show_extra(self):
        cookie_name = '%s-show-extra-%s' % (
            self.section,
            self.current_userid
        )
        return self.request.get(cookie_name, '').split('|')

    def archived_documents_shown(self):
        """
        Tell if we should show archived documents or not
        """
        return 'archived_documents' in self.show_extra

    def archived_tags_shown(self):
        """
        Tell if we should show archived tags or not
        """
        return 'archived_tags' in self.show_extra

    def events(self):
        """
        Return the events in this workspace
        to be shown in the events section of the sidebar
        """
        catalog = api.portal.get_tool('portal_catalog')
        workspace = self.root
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

    def format_event_date(self, event):
        return format_event_date_for_title(event)


class SidebarDocuments(Sidebar):
    ''' Customized tile that shows only the Documents
    '''
    index = ViewPageTemplateFile('templates/sidebar-documents.pt')
    can_slides = True

    @property
    @memoize
    def current_label(self):
        ''' Return the label (aka tag or subject) that we are exploring
        '''
        if not self.grouping().startswith('label'):
            return
        groupname = self.request.get('groupname')
        if not groupname:
            return
        if groupname == 'Untagged':
            return
        return groupname

    @property
    @memoize
    def autotag_bulk_uploaded(self):
        ''' Check if we should activate the autotag feature
        on the bulk uploaded files
        '''
        return self.current_label

    @property
    @memoize
    def bulk_upload_url(self):
        params = {
            '_authenticator': createToken(),
        }
        if self.autotag_bulk_uploaded:
            params['groupname'] = self.current_label
        return '{url}/workspaceFileUpload?{qs}'.format(
            url=self.context.absolute_url(),
            qs=urlencode(params),
        )


class SidebarEvents(Sidebar):
    ''' Customized tile that shows only the Events
    '''
    index = ViewPageTemplateFile('templates/sidebar-events.pt')

    def shorten(self, text):
        return shorten(text, length=256)


class SidebarTodos(Sidebar):
    ''' Customized tile that shows only the Todos
    '''
    index = ViewPageTemplateFile('templates/sidebar-todos.pt')
