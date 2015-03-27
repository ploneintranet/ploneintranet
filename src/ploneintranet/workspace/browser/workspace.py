from Products.Five import BrowserView
from plone import api
from plone.memoize.forever import memoize
from zope.interface import implements
from plone.app.blocks.interfaces import IBlocksTransformEnabled
from ploneintranet.workspace.interfaces import IWorkspaceState
from ploneintranet.workspace.utils import parent_workspace


class BaseWorkspaceView(BrowserView):
    """
    Base view class for workspace related view
    """
    @memoize
    def workspace(self):
        """Acquire the root workspace of the current context"""
        return parent_workspace(self.context)


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
