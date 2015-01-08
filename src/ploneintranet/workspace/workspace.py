from zope.interface import implements
from plone.memoize.view import memoize
from Products.Five.browser import BrowserView
from interfaces import IWorkspaceState
from ploneintranet.workspace.utils import parent_workspace
from plone import api


class WorkspaceView(BrowserView):
    """
    Default View of the workspace
    """

    def workspace(self):
        # return the related workspace
        return parent_workspace(self.context)


class WorkspaceState(BrowserView):
    """
    Information about the state of the workspace
    """

    implements(IWorkspaceState)

    @memoize
    def workspace(self):
        # Attempt to acquire the current workspace
        return parent_workspace(self.context)

    @memoize
    def state(self):
        if self.workspace() is not None:
            return api.content.get_state(self.workspace())
