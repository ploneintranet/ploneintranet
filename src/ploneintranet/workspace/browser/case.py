from ploneintranet.workspace.interfaces import IMetroMap
from ploneintranet.workspace.browser.workspace import WorkspaceView
from ploneintranet.workspace.config import TRANSITION_ICONS


class CaseView(WorkspaceView):
    """Variant of the WorkspaceView with additional methods for Case Workspaces
    """

    @property
    def transition_icons(self):
        return TRANSITION_ICONS

    @property
    def metromap_sequence(self):
        return IMetroMap(self.context).metromap_sequence
