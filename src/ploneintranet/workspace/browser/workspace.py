from Products.Five import BrowserView
from plone import api
from plone.app.blocks.interfaces import IBlocksTransformEnabled
from plone.memoize.forever import memoize
from ploneintranet.workspace.interfaces import IWorkspaceState
from ploneintranet.workspace.utils import parent_workspace
from zope.interface import implements

import json


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
            obj=self,
        )


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


class WorkspaceMembersJSONView(BrowserView):
    """
    Return member details in JSON
    """
    def __call__(self):
        users = self.context.existing_users()
        member_details = []
        for user in users:
            member_details.append({
                'text': user['title'] or user['id'],
                'id': user['id'],
            })
        return json.dumps(member_details)
