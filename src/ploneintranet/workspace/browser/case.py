from Products.Five import BrowserView
from plone import api
from plone.memoize.view import memoize

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

    @property
    def transition_icons(self):
        context = self.context
        workflow = IMetroMap(context)._metromap_workflow
        if not workflow:
            return {}
        if 'transition_icons' in workflow.variables:
            return workflow.getInfoFor(context, 'transition_icons', {})
        else:
            return {}


class CaseWorkflowGuardView(BrowserView):
    """Enable transition to the next workflow state when there are no open
    tasks
    """

    @memoize
    def __call__(self):
        context = self.context
        catalog = api.portal.get_tool('portal_catalog')
        current_path = '/'.join(context.getPhysicalPath())
        brains = catalog(
            path=current_path,
            portal_type='todo',
            review_state='open',
        )
        has_no_open_tasks = len(brains) == 0
        return has_no_open_tasks
