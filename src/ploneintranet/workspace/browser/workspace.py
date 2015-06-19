from Products.Five import BrowserView
from plone import api
from plone.memoize.view import memoize
from zope.interface import implements
from plone.app.blocks.interfaces import IBlocksTransformEnabled
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


class AllUsersJSONView(BrowserView):
    """
    Return all users in JSON for use in picker
    """
    def __call__(self):
        q = self.request.get('q', '')
        users = api.user.get_users()
        member_details = []
        for user in users:
            fullname = user.getProperty('fullname')
            email = user.getProperty('email')
            uid = user.getProperty('id')
            if q in fullname or q in email or q in uid:
                member_details.append({
                    'text': '%s <%s>' % (fullname, email),
                    'id': uid,
                })
        return dumps(member_details)
