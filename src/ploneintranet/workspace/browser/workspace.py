from Products.Five import BrowserView
from Products.Five.utilities.marker import mark
from plone import api
from plone.app.blocks.interfaces import IBlocksTransformEnabled
from plone.memoize.forever import memoize
from ploneintranet.workspace.interfaces import ICase
from ploneintranet.workspace.interfaces import IMetroMap
from ploneintranet.workspace.interfaces import IWorkspaceState
from ploneintranet.workspace.utils import parent_workspace
from zope.interface import implements


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


class CaseWorkspaceView(WorkspaceView):
    """Variant of the WorkspaceView with additional methods for Case Workspaces
    """
    @property
    def metromap_sequence(self):
        return IMetroMap(self.context).metromap_sequence

class WorkspaceState(BaseWorkspaceView):
    """
    Information about the state of the workspace
    """

    implements(IWorkspaceState)

    @memoize
    def state(self):
        if self.workspace() is not None:
            return api.content.get_state(self.workspace())


class SwitchToCaseView(BrowserView):
    """
    Set the ICase interface on a Workspace
    """

    def __call__(self):
        mark(self.context, ICase)
