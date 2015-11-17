from Products.Five import BrowserView
from plone import api
from plone.memoize.view import memoize

from ploneintranet.workspace.interfaces import IMetroMap
from ploneintranet.workspace.browser.workspace import WorkspaceView
from ploneintranet.workspace.config import TRANSITION_ICONS
from ploneintranet.workspace.utils import parent_workspace


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
        if mm_seq[milestone_id].get('finished'):
            state = 'finished'
        elif is_last and mm_seq[second_last_milestone_id].get('finished'):
            tasks = self.context.tasks()
            if not tasks[milestone_id]:
                state = 'finished'
        return state


class CaseWorkflowGuardView(BrowserView):
    """Enable transition to the next workflow state when there are no open
    tasks
    """

    @memoize
    def __call__(self):
        workspace = parent_workspace(self.context)
        wft = api.portal.get_tool('portal_workflow')
        case_milestone = wft.getInfoFor(workspace, 'review_state')

        catalog = api.portal.get_tool('portal_catalog')
        workspace_path = '/'.join(workspace.getPhysicalPath())
        open_tasks = catalog(
            path=workspace_path,
            portal_type='todo',
            review_state='open',
        )
        # Only prevent the current milestone from being closed if there are
        # open tasks assigned to the current milestone.
        # This ignores open tasks assigned to earlier milestones since they
        # aren't represented in the metromap.
        for task in open_tasks:
            if task.getObject().milestone == case_milestone:
                return False
        return True
