# coding=utf-8
from plone import api
from plone.memoize.view import memoize
from plone.tiles import Tile
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from Products.CMFCore.Expression import getExprContext


class MetromapTile(Tile):
    ''' Base view to render a metromap
    '''
    default_transition_icons = {
        'assign': 'icon-right-hand',
        'finalise': 'icon-pin',
        'request': 'icon-right-circle',
        'submit': 'icon-right-circle',
        'decide': 'icon-hammer',
        'close': 'icon-cancel-circle',
        'archive': 'icon-archive',
    }

    @property
    @memoize
    def workspace_view(self):
        ''' Retun the workspace tasks
        '''
        return api.content.get_view(
            'view',
            self.context,
            self.request,
        )

    @memoize
    def get_avatar_tag(self, userid):
        ''' Return the workspace tasks
        '''
        return self.workspace_view.get_avatar_tag(userid)

    @property
    @memoize
    def tasks(self):
        ''' Return the workspace tasks as a property
        '''
        return self.workspace_view.tasks()

    @property
    @memoize
    def workflow(self):
        '''All Case Workspaces should have a placeful workflow. In order to
        render the metromap, this workflow needs to have a metromap_transitions
        variable which determines the order of the milestones (states) and the
        transitions between them.
        Return the workflow required to render the metromap.
        '''
        pw = api.portal.get_tool('portal_workflow')
        workflows = pw.getWorkflowsFor(self.context)
        for workflow in workflows:
            if workflow.variables.get('metromap_transitions', False):
                return workflow

    @property
    @memoize
    def transition_icons(self):
        ''' Retun a mapping to get the icons for the metromap transitions
        '''
        workflow = self.workflow
        if not workflow:
            return {}
        return workflow.getInfoFor(
            self.context,
            'transition_icons',
            self.default_transition_icons
        )

    @property
    @memoize
    def transitions(self):
        ''' A data structure is stored as a TAL expression on a workflow which
        determines the sequence of workflow states/milestones used to render
        the metromap.
        We need to evaluate the expression and returns the data structure.
        It consists of a list of dicts each with the workflow state, the
        transition to the next milestone in the metromap, and the
        transition required to return to the milestone:
        [{
          'state': 'new',
          'next_transition': 'finalise',
          'reopen_transition': 'reset'
        }, {
          'state': 'complete',
          'next_transition': 'archive',
          'reopen_transition': 'finalise'
        }, {
          'state': 'archived'}
        ]
        '''
        metromap_workflow = self.workflow
        if metromap_workflow is None:
            return []
        wfstep = metromap_workflow.variables["metromap_transitions"]
        return wfstep.default_expr(getExprContext(self.context))

    def get_milestone(self, transition):
        ''' Get a milestone from a transition
        '''
        state = transition['state']
        next_transition = transition.get('next_transition')
        back_transition = transition.get('reopen_transition')
        if next_transition:
            transition_title = _(
                self.workflow.transitions.get(next_transition).title
            )
        else:
            transition_title = ''
        milestone = {
            'state': state,
            'title': _(self.workflow.states.get(state).title),
            'tasks': self.tasks.get(state, []),
            'icon': self.transition_icons.get(next_transition, ''),
            'transition_id': next_transition,
            'transition_title': transition_title,
            'back_transition_id': back_transition,
        }
        return milestone

    def tasks_are_all_completed(self, tasks):
        ''' Check if the current taask has open review_states
        '''
        for task in tasks:
            if not task['checked']:
                return False
        return True

    @property
    @memoize
    def metromap_state(self):
        ''' This is the state reached in the metromap journey

        It may be different from the actual review state if the case is frozen
        '''
        # If the case is frozen, render the MetroMap for the pre-frozen state
        freeze_view = api.content.get_view(
            'freeze-view',
            self.context,
            self.request,
        )
        return freeze_view.metromap_state

    def set_milestone_states(self, milestones):
        ''' Check if the transition is finished or not and set this as state
        in the milestone
        '''
        metromap_state = self.metromap_state

        # We start from the end and declare that the transition is unfinished
        finished = 'unfinished'
        for idx, milestone in enumerate(reversed(milestones)):
            is_last = idx == 0
            is_current = milestone['state'] == metromap_state
            all_tasks_completed = self.tasks_are_all_completed(
                milestone['tasks']
            )
            if is_current and is_last and all_tasks_completed:
                # if we are at the end of the journey, everything is finished
                finished = 'finished'

            milestone['is_current'] = is_current
            milestone['finished'] = finished
            milestone['all_tasks_completed'] = all_tasks_completed

            if is_current:
                # if we are at this point,
                # the other milestones have been completed
                finished = 'finished'

    @property
    @memoize
    def milestones(self):
        ''' Return the metromap milestones for rendering
        '''
        milestones = []
        milestones = map(self.get_milestone, self.transitions)
        self.set_milestone_states(milestones)
        return milestones

    @memoize
    def get_milestone_options(self, selected_value=None):
        ''' Return the options for a milestone select
        '''
        if selected_value is None:
            selected_value = self.request.form.get('milestone')
        options = []
        get_state = self.workflow.states.get
        for transition in self.transitions:
            value = transition['state']
            title = _(get_state(value).title)
            selected = 'selected' if value == selected_value else None
            options.append({
                'value': value,
                'title': title,
                'selected': selected
            })
        return options
