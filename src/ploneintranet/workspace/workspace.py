from zope.interface import implements
from plone.memoize.view import memoize
from Products.Five.browser import BrowserView
from interfaces import IWorkspaceState
from ploneintranet.workspace.workspacefolder import IWorkspaceFolder
from plone import api

from Acquisition import aq_chain


class WorkspaceState(BrowserView):
    """
    Information about the state of the workspace
    """

    implements(IWorkspaceState)

    @memoize
    def workspace(self):
        # Attempt to acquire the current workspace
        if IWorkspaceFolder.providedBy(self.context):
            return self.context
        for parent in aq_chain(self.context):
            if IWorkspaceFolder.providedBy(parent):
                return parent

    @memoize
    def state(self):
        if self.workspace() is not None:
            return api.content.get_state(self.workspace())
