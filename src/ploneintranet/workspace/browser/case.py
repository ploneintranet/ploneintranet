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

    def milestone_state(self, milestone_id):
        """
        Determine whether the milestone should be considered finished or not.

        If it is the last milestone and it has no tasks, the final node should
        be considered finished so that the line is all green.
        """
        mm_seq = self.metromap_sequence
        milestone_ids = mm_seq.keys()
        is_last = milestone_id == milestone_ids[-1]
        second_last_milestone_id = milestone_ids[-2]
        state = 'unfinished'
        if mm_seq[milestone_id]['finished']:
            state = 'finished'
        elif is_last and mm_seq[second_last_milestone_id]['finished']:
            tasks = self.context.tasks()
            if not tasks[milestone_id]:
                state = 'finished'
        return state
