# coding=utf-8
from Acquisition import aq_inner
from collections import defaultdict
from collective.workspace.interfaces import IWorkspace
from datetime import date
from json import dumps
from plone import api
from plone.app.blocks.interfaces import IBlocksTransformEnabled
from plone.memoize.view import memoize
from ploneintranet import api as pi_api
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.layout.utils import get_record_from_registry
from ploneintranet.search.interfaces import ISiteSearch
from ploneintranet.todo.behaviors import ITodo
from ploneintranet.workspace.behaviors.group import IMembraneGroup
from ploneintranet.workspace.behaviors.group import MembraneWorkspaceGroup
from ploneintranet.workspace.interfaces import IBaseWorkspaceFolder
from ploneintranet.workspace.interfaces import IGroupingStorage
from ploneintranet.workspace.interfaces import IWorkspaceFolder
from ploneintranet.workspace.interfaces import IWorkspaceState
from ploneintranet.workspace.policies import PARTICIPANT_POLICY
from ploneintranet.workspace.utils import parent_workspace
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from Products.membrane.interfaces import group as group_ifaces
from Products.PlonePAS.interfaces.group import IGroupData
from zope.component import getAdapter
from zope.component import getUtility
from zope.component.interfaces import ComponentLookupError
from zope.interface import implements


class BaseWorkspaceView(BrowserView):
    """
    Base view class for workspace related view
    """
    @property
    @memoize
    def is_ajax(self):
        ''' Check if we have an ajax call
        '''
        requested_with = self.request.environ.get('HTTP_X_REQUESTED_WITH')
        return requested_with == 'XMLHttpRequest'

    @property
    @memoize
    def include_clicktracker(self):
        """Is inclusion of slcclicktracker element enabled in the registry?"""
        include_slcclicktracker = get_record_from_registry(
            'ploneintranet.workspace.include_slcclicktracker',
            False)
        return include_slcclicktracker

    @property
    @memoize
    def show_sidebar(self):
        ''' Should we show the sidebar?
        '''
        form = self.request.form
        if 'show_sidebar' in form:
            return True
        if 'hide_sidebar' in form:
            return False
        return True

    @memoize
    def workspace(self):
        """Acquire the root workspace of the current context"""
        return parent_workspace(self.context)

    def can_manage_workspace(self):
        """
        does this user have permission to manage the workspace
        """
        return api.user.has_permission(
            "ploneintranet.workspace: Manage workspace",
            obj=self.context,
        )

    def can_add_status_updates(self):
        """
        Does this user have the permission to add status updates
        """
        return api.user.has_permission(
            "Plone Social: Add Microblog Status Update",
            obj=self.context)

    @property
    @memoize
    def groupids_key_mapping(self):
        ''' Return the set of the group ids knows by portal_groups
        '''
        if not self.groups_container:
            return {}
        return {
            group.getGroupId(): key
            for key, group in self.groups_container.objectItems()
        }

    @memoize
    def get_principal_title(self, principal):
        ''' Get the title for this principal
        '''
        if isinstance(principal, basestring):
            principalid = principal
            principal = self.resolve_principalid(principal)
            if principal is None:
                return principalid
        if (
                IGroupData.providedBy(principal) or
                isinstance(principal, MembraneWorkspaceGroup)
        ):
            return principal.getGroupName()
        if hasattr(principal, 'getGroupId'):
            return principal.Title() or principal.getGroupId()
        if IWorkspaceFolder.providedBy(principal):
            return principal.Title()
        return (
            getattr(principal, 'fullname', '') or
            principal.getProperty('fullname') or
            principal.getId()
        )

    def get_principal_url(self, principal):
        ''' Get a suitable URL for viewing this principal
        '''
        if isinstance(principal, basestring):
            principal = self.resolve_principalid(principal)
        if (
                IGroupData.providedBy(principal) or
                isinstance(principal, MembraneWorkspaceGroup)
        ):
            portal = api.portal.get()
            p_url = portal.absolute_url()
            return "{0}/workspace-group-view?id={1}".format(
                p_url, principal.getId())
        return principal.absolute_url()

    @memoize
    def get_principal_description(self, principal):
        ''' Get the description for this principal
        '''
        if isinstance(principal, basestring):
            principal = self.resolve_principalid(principal)
        if not hasattr(principal, 'getGroupId'):
            return ''
        group_memberids = set(principal.getGroupMembers())
        group_groupids = group_memberids.intersection(
            self.groupids_key_mapping
        )
        return _(
            u"number_of_members",
            default=u'${no_users} Users / ${no_groups} Groups',
            mapping={
                u'no_users': len(group_memberids) - len(group_groupids),
                u'no_groups': len(group_groupids)
            }
        )

    @memoize
    def get_principal_roles(self, principal):
        ''' Get the description for this principalid
        '''
        adapter = IWorkspace(self.context)
        if hasattr(principal, 'getGroupId'):
            groups = adapter.get(principal.getGroupId()).groups
        else:
            groups = adapter.get(principal.getId()).groups

        if 'Admins' in groups:
            return ['Admin']

        # The policies are ordered from the less permissive to the most
        # permissive. We reverse them
        for policy in reversed(PARTICIPANT_POLICY):
            # BBB: code copied from the workspacefolder existing_users function
            # at 58c758d20a820dcb9f691168a9215bfc9741b00e
            # not really clear to me why we are skipping the current policy
            if policy != self.context.participant_policy:
                if policy.title() in groups:
                    # According to the design there is at most one extra role
                    # per user, so we go with the first one we find. This may
                    # not be enforced in the backend though.
                    return [PARTICIPANT_POLICY[policy]['title']]

        if groups == {'Guests'}:
            return ['Guest']
        return []

    def principal_sorting_key(self, principal):
        ''' First we want the groups, the we want alphabetical sorting
        '''
        is_group = hasattr(principal, 'getGroupId')
        return (not is_group, self.get_principal_title(principal))

    @property
    @memoize
    def groups_container(self):
        ''' Returns the group container (if found) or an empty dictionary
        '''
        portal = api.portal.get()
        return portal.get('groups', {})

    @property
    @memoize
    def workspaces_container(self):
        ''' Returns the workspaces container (if found) or an empty dictionary
        '''
        portal = api.portal.get()
        return portal.get('workspaces', {})

    @property
    @memoize
    def users_container(self):
        ''' Returns the group container (if found) or an empty dictionary
        '''
        portal = api.portal.get()
        return portal.get('profiles', {})

    @memoize
    def resolve_principalid(self, principalid):
        ''' Given a principal id, tries to get him for profile or groups folder
        and then look for him with pas.
        '''
        principal = (
            self.users_container.get(principalid) or
            self.workspaces_container.get(principalid) or
            self.groups_container.get(
                self.groupids_key_mapping.get(principalid)
            ) or
            api.user.get(principalid) or
            api.group.get(principalid)
        )
        if IMembraneGroup.providedBy(principal):
            principal = MembraneWorkspaceGroup(principal)
        return principal

    @property
    @memoize
    def guest_ids(self):
        ''' Get the valid member ids through IWorkspace
        '''
        adapter = IWorkspace(self.context)
        return [
            principalid for principalid in self.member_ids
            if adapter.get(principalid).groups == {'Guests'}
        ]

    @property
    @memoize
    def member_ids(self):
        ''' Get the valid member ids through IWorkspace
        '''
        principalids = IWorkspace(self.context).members
        return filter(self.resolve_principalid, principalids)

    @property
    @memoize
    def principals(self):
        ''' Return the list of principals which are assigned to this context
        '''
        objs = map(self.resolve_principalid, self.member_ids)
        return objs

    def get_sorted_principals(self, sort_by='last_name'):
        objs = self.principals
        return sorted(objs, key=lambda user: getattr(user, sort_by, None))

    @memoize
    def guests(self):
        ''' Return the list of principals which are guests in this context
        By design they are assigned through the sharing view
        '''
        objs = map(self.resolve_principalid, self.guest_ids)
        return objs

    @memoize
    def get_avatar_tag(self, userid):
        ''' Get's and caches the userprofile
        '''
        return pi_api.userprofile.avatar_tag(
            userid,
            link_to='profile'
        )

    @memoize
    def tasks(self):
        ''' Get the context tasks
        '''
        is_case = self.context.is_case
        items = defaultdict(list) if is_case else []
        wft = api.portal.get_tool('portal_workflow')
        ptype = 'todo'
        brains = api.content.find(
            context=self.context,
            portal_type=ptype,
            sort_on=['due', 'getObjPositionInParent'],
        )
        today = date.today()
        for brain in brains:
            obj = brain.getObject()
            todo = ITodo(obj)
            done = wft.getInfoFor(todo, 'review_state') == u'done'
            overdue = False
            if not done and todo.due:
                overdue = todo.due < today
            data = {
                'id': brain.UID,
                'title': brain.Title,
                'description': brain.Description,
                'url': brain.getURL(),
                'checked': done,
                'due': todo.due,
                'overdue': overdue,
                'obj': obj,
                'can_edit': api.user.has_permission(
                    'Modify portal content', obj=obj),
            }
            if is_case:
                milestone = "unassigned"
                if obj.milestone not in ["", None]:
                    milestone = obj.milestone
                items[milestone].append(data)
            else:
                items.append(data)
        if is_case:
            for milestone in items.keys():
                # Show the checked tasks before the unchecked tasks
                items[milestone].sort(key=lambda x: x['checked'] is False)
        return items

    @memoize
    def get_related_workspaces(self):
        ''' Resolve the related workspaces brains
        '''
        related_workspaces = getattr(self.context, 'related_workspaces', [])
        if not related_workspaces:
            return []
        brains = api.content.find(UID=related_workspaces)
        return brains


class WorkspaceView(BaseWorkspaceView):
    """
    Default View of the workspace
    """
    implements(IBlocksTransformEnabled)


class WorkspaceState(BaseWorkspaceView):
    """
    Information about the state of the workspace
    """

    implements(IWorkspaceState)

    @memoize
    def state(self):
        if self.workspace() is not None:
            return api.content.get_state(self.workspace())


def format_users_json(users):
    """
    Format a list of users as JSON for use with pat-autosuggest

    :param list users: A list of user brains
    :rtype string: JSON {"user_id1": "user_title1", ...}
    """
    formatted_users = []
    for user in users:
        fullname = safe_unicode(user.Title)
        email = safe_unicode(user.email)
        uid = user.getId
        formatted_users.append({
            'id': uid,
            'text': u'{0} <{1}>'.format(fullname, email),
        })
    return dumps(formatted_users)


class WorkspaceMembersJSONView(BrowserView):
    """
    Return workspace members in JSON for use with pat-autosuggest.
    Only members of the current workspace are found.
    """
    def __call__(self):
        q = safe_unicode(self.request.get('q', '').strip())
        if not q:
            return ""
        query = {'SearchableText': u'{0}*'.format(q)}
        users = pi_api.userprofile.get_users(
            context=self.context, full_objects=False, **query)
        return format_users_json(users)


class AllUsersJSONView(BrowserView):
    """
    Return a filtered list of users for pat-autosuggest.
    Any user can be found, not only members of the current workspace
    """
    def __call__(self):
        q = safe_unicode(self.request.get('q', '').strip())
        if not q:
            return ""
        query = {'SearchableText': u'{0}*'.format(q)}
        users = pi_api.userprofile.get_user_suggestions(
            context=self.context, full_objects=False, **query)
        return format_users_json(users)


class BrainToGroupAdapter(object):
    ''' Make a brain behave like a group
    '''

    def __init__(self, context):
        self.context = context

    def getId(self):
        ''' Return this group id
        '''
        return self.context.getGroupId

    def getProperty(self, key, fallback=''):
        ''' Mimic getProperty, remapping some keys
        '''
        if key == 'state':
            key = 'review_state'
        elif key == 'title':
            key = 'Title'
        return getattr(self.context, key, fallback)


class AllGroupsJSONView(BrowserView):
    """
    Return all groups in JSON for use in picker
    TODO: consolidate AllGroupsJSONView with AllUsersJSONView
    """

    def get_groups(self):
        ''' Return all the groups
        '''
        only_membrane_groups = get_record_from_registry(
            'ploneintranet.userprofile.only_membrane_groups',
            False
        )
        if only_membrane_groups:
            mt = api.portal.get_tool(name='membrane_tool')
            purl = api.portal.get_tool(name='portal_url')
            groups = map(
                BrainToGroupAdapter,
                mt.unrestrictedSearchResults(
                    object_implements=(group_ifaces.IGroup.__identifier__),
                    path=purl.getPortalPath()
                )
            )
        else:
            groups = api.group.get_groups()
        return groups

    def __call__(self):
        q = self.request.get('q', '').lower()

        groups = self.get_groups()

        group_details = []
        ws = IWorkspace(self.context)
        for group in groups:
            groupid = group.getId()
            # XXX Filter out groups representing workspace roles. Review
            # whether we need/want this and/or can do it more efficiently.
            if (
                groupid == self.context.id or  # don't add group to itself
                group.getProperty('state') == 'secret' or
                groupid.partition(':')[0] in ws.available_groups
            ):
                continue
            title = group.getProperty('title') or groupid
            email = group.getProperty('email')
            if email:
                title = '%s <%s>' % (title, email)
            description = group.getProperty('description') or ''
            if q in title.lower() or q in description.lower():
                group_details.append({
                    'text': title,
                    'id': groupid,
                })
        return dumps(group_details)


class AllUsersAndGroupsJSONView(BrowserView):
    def __call__(self):
        q = self.request.get('q', '').strip()
        if not q:
            return ""
        acl_users = api.portal.get_tool('acl_users')
        results = []
        groups = {x['id']: x['title'] for x in acl_users.searchGroups(id=q)}
        groups.update(
            {x['id']: x['title'] for x in acl_users.searchGroups(name=q)})
        if groups:
            for id, title in groups.items():
                text = title or id
                results.append({'id': id, 'text': text})
        query = {'SearchableText': u'{0}*'.format(safe_unicode(q))}
        users = pi_api.userprofile.get_users(full_objects=False, **query)
        for user in users:
            fullname = user.Title
            email = user.email
            results.append({
                'id': user.getId,
                'text': u'{0} <{1}>'.format(fullname, email),
            })
        return dumps(results)


class ReorderTags(BrowserView):
    """ Lets the workspace manager re-order the tags inside a workspace """

    def __call__(self):
        context = aq_inner(self.context)
        try:
            gs = getAdapter(context, IGroupingStorage)
        except ComponentLookupError:
            return u"Could not get adapter for context: %s"  \
                % context.absolute_url()
        self.tags = [tag for tag in gs.get_order_for('label')]
        if self.request.get('batch-function') == 'save':
            myorder = self.request.get('tags_order') or []
            if 'Untagged' in myorder:
                myorder.remove('Untagged')

            gs.set_order_for('label', myorder)
            return self.request.response.redirect(
                self.context.absolute_url() + '/@@sidebar.documents'
            )
        else:
            return self.index()


def format_workspaces_json(workspaces, skip=[]):
    """
    Format a list of workspaces as JSON for use with pat-autosuggest

    :param list workspaces: A list of brains
    :param lis skip: A list of UIDs to skip
    :rtype string: JSON {"ws_id1": "ws_title1", ...}
    """
    formatted_ws = []
    for ws in workspaces:
        uid = ws.UID
        if uid in skip:
            continue
        title = safe_unicode(ws['Title'])
        formatted_ws.append({
            'id': uid,
            'text': title,
        })
    return dumps(formatted_ws)


class WorkspacesJSONView(BrowserView):
    """
    Return a filtered list of workspaces for pat-autosuggest.
    Any workspace can be found.
    """
    def __call__(self):
        q = safe_unicode(self.request.get('q', '').strip())
        if not q:
            return ""
        query = {'phrase': u'{0}*'.format(q),
                 'filters': self.get_filters(),
                 'step': 50,
                 }

        search_util = getUtility(ISiteSearch)
        workspaces = search_util.query(**query)
        workspaces = sorted(workspaces, key=lambda ws: ws['Title'])
        skip = self.get_skip()
        return format_workspaces_json(workspaces, skip)

    def get_filters(self):
        return {
            'object_provides': 'collective.workspace.interfaces.IHasWorkspace',
        }

    def get_skip(self):
        return []


class RelatedWorkspacesJSONView(WorkspacesJSONView):
    """
    Return a filtered list of workspaces for pat-autosuggest.
    Current workspace and its related workspaces are excluded.
    """

    def get_skip(self):
        skip = []
        if IBaseWorkspaceFolder.providedBy(self.context):
            skip = getattr(self.context, 'related_workspaces', []) or []
            skip.append(self.context.UID())
        return skip


class WorkspaceCalendarView(BaseWorkspaceView):
    """
    Wrapper to include the fullcalendar tile on workspaces
    """
    implements(IBlocksTransformEnabled)
