from ploneintranet.workspace.interfaces import IMetroMap
from ploneintranet.workspace.browser.workspace import WorkspaceView


class CaseView(WorkspaceView):
    """Variant of the WorkspaceView with additional methods for Case Workspaces
    """

    @property
    def transition_icons(self):
        return {
            'transfer_to_department': 'icon-right-hand',
            'finalise': 'icon-pin',
            'submit': 'icon-right-circle',
            'decide': 'icon-hammer',
            'close': 'icon-cancel-circle',
            'archive': 'icon-archive',
        }

    @property
    def metromap_sequence(self):
        return IMetroMap(self.context).metromap_sequence
