from Products.Five import BrowserView
from collective.workspace.interfaces import IWorkspace
from plone import api
from plone.memoize.view import memoize
from zope.interface import implements
from plone.app.blocks.interfaces import IBlocksTransformEnabled
import ploneintranet.api as pi_api
from ploneintranet.workspace.interfaces import IWorkspaceState
from ploneintranet.workspace.utils import parent_workspace
from json import dumps


class BaseWorkspaceView(BrowserView):
    """
    Base view class for workspace related view
    """
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


def filter_users_json(query, users):
    """
    Filter a list of users, by a query string and return the results as JSON.
    For use with pat-autosuggest.

    :param str query: The search query
    :param list users: A list of user objects
    :rtype string: JSON {"user_id1": "user_title1", ...}
    """
    filtered_users = []
    for user in users:
        fullname = user.getProperty('fullname')
        email = user.getProperty('email')
        uid = user.getProperty('id')
        user_string = '{} {} {}'.format(fullname, email, uid)
        if query.lower() in user_string.lower():
            filtered_users.append({
                'id': uid,
                'text': '{} <{}>'.format(fullname, email),
            })
    return dumps(filtered_users)


class WorkspaceMembersJSONView(BrowserView):
    """
    Return workspace members in JSON for use with pat-autosuggest.
    """
    def __call__(self):
        members = IWorkspace(self.context).members
        users = []
        for member in members:
            user = api.user.get(member)
            if user:
                users.append(user)
        q = self.request.get('q', '')
        return filter_users_json(q, users)


class AllUsersJSONView(BrowserView):
    """
    Return a filtered list of users for pat-autosuggest
    """
    def __call__(self):
        q = self.request.get('q', '')
        user_details = []
        for user in pi_api.userprofile.get_users(
                SearchableText=u'{}*'.format(q)):
            fullname = user.Title()
            email = user.email
            user_details.append({
                'id': user.getId(),
                'text': u'{} <{}>'.format(fullname, email),
            })
        return dumps(user_details)


class AllGroupsJSONView(BrowserView):
    """
    Return all groups in JSON for use in picker
    TODO: consolidate AllGroupsJSONView with AllUsersJSONView
    """
    def __call__(self):
        q = self.request.get('q', '').lower()
        groups = api.group.get_groups()
        group_details = []
        ws = IWorkspace(self.context)
        for group in groups:
            groupid = group.getId()
            # XXX Filter out groups representing workspace roles. Review
            # whether we need/want this and/or can do it more efficiently.
            skip = False
            for special_group in ws.available_groups:
                if groupid.startswith('{}:'.format(special_group)):
                    skip = True
            if skip:
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
