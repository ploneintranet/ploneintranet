# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from plone import api
from plone.api.exc import InvalidParameterError
from plone.memoize.view import memoize
from Products.Five import BrowserView


class WorkflowMenu(BrowserView):
    ''' The helper view the renders the workflow select
    '''
    _edit_permission = 'Modify portal content'
    _review_permission = 'Review portal content'

    @property
    @memoize
    def can_edit(self):
        ''' Check if the user can edit
        '''
        return api.user.has_permission(
            self._edit_permission,
            obj=self.context
        )

    @property
    @memoize
    def can_review(self):
        return self.can_edit or api.user.has_permission(
            self._review_permission,
            obj=aq_inner(self.context)
        )

    @property
    @memoize
    def wf_tool(self):
        return api.portal.get_tool('portal_workflow')

    @memoize
    def _get_active_workflows(self):
        return self.wf_tool.getWorkflowsFor(aq_inner(self.context))

    @memoize
    def has_workflow(self):
        return len(self._get_active_workflows()) > 0

    @memoize
    def get_workflow_state(self):
        return api.content.get_state(obj=aq_inner(self.context))

    @memoize
    def get_workflow_transitions(self):
        ''' Return possible workflow transitions and destination state names
        '''
        context = aq_inner(self.context)
        # This check for locked state was copied from star - unclear if needed
        try:
            locking_info = api.content.get_view(
                'plone_lock_info', self.context, self.request)
        except InvalidParameterError:
            locking_info = None
        if locking_info and locking_info.is_locked_for_current_user():
            return []

        current_state_id = self.get_workflow_state()

        if current_state_id is None:
            return []

        available_states = self._get_active_workflows()[0].states

        current_state = getattr(available_states, current_state_id).title
        states = [dict(
            action='',
            current_state_id=current_state_id,
            title=current_state or current_state_id,
            new_state_id='',
            selected='selected')]

        workflow_actions = self.wf_tool.listActionInfos(object=context)
        states_id = [item['new_state_id'] for item in states]
        for action in workflow_actions:
            if action['category'] != 'workflow':
                continue
            new_state_id = action['transition'].new_state_id
            # Only target states are shown in the UI. If two transitions lead
            # to the same state we want to show the state only once.
            if new_state_id not in states_id:
                title = getattr(available_states, new_state_id).title
                states.append(dict(
                    action=action['id'],
                    title=title,
                    new_state_id=new_state_id,
                    selected=None,
                ))
        return sorted(states, key=lambda x: x['title'])

    @property
    @memoize
    def injection_url(self):
        ''' The url to get this view
        '''
        return '/'.join((
            self.context.absolute_url(),
            'view',
        ))

    def form_pat_inject_options(self):
        ''' Return the data-path-inject options we want to use
        '''
        template = ' && '.join((
            'url: {url}; source: #global-statusmessage; target: #global-statusmessage;',  # noqa
            'url: {url}; source: #document-body; target: #document-body;',
        ))
        return template.format(
            url=self.injection_url,
        )
