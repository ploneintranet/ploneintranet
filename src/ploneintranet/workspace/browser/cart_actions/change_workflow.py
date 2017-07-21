# -*- coding: utf-8 -*-
"""A Cart Action for changing the workflow state of all items listed in cart"""

from Acquisition import aq_inner
from plone import api
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.workspace.browser.cart_actions.base import BaseCartView
from Products.CMFCore.interfaces._content import IFolderish
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ZODB.POSException import ConflictError


class ChangeWorkflowView(BaseCartView):
    """Change Workflow Action implementation"""

    title = _('Batch change workflow')

    def confirm(self):
        index = ViewPageTemplateFile("templates/change_workflow_confirmation.pt")  # noqa
        return index(self)

    def get_transitions(self):
        """
            Following the paradigm for workflow menues, we need to show the
            title of the intended new state instead of the transition name.
        """
        states = []
        pworkflow = api.portal.get_tool('portal_workflow')
        workflows = set()
        for obj in self.items:
            workflows = workflows.union(
                {wf for wf in pworkflow.getWorkflowsFor(aq_inner(obj))})
        available_states = {}
        for wf in workflows:
            for id, state in wf.states.objectItems():
                available_states[id] = state

        for obj in self.items:
            for action in pworkflow.listActionInfos(object=obj):
                if action['category'] != 'workflow':
                    continue
                new_state = action['transition'].new_state_id
                # Only target states are shown in the UI. If two transitions
                # lead to the same state we want to show the state only once.
                if new_state not in [item['new_state'] for item in states]:
                    title = available_states[new_state].title
                    states.append(dict(
                        action=action['id'],
                        title=title,
                        new_state=new_state,
                    ))
        return states

    def change_workflow(self):
        """ Attempt to change the workflow of selected items

        """
        handled = []
        uids = self.request.form.get('uids', [])
        transition_id = self.request.form.get('transition', '')
        if not len(uids):
            api.portal.show_message(
                message=_(u"Please select at least one item."),
                request=self.request,
                type="warning")

        # We set recursive to be generally True
        # See discussion on quaive/ploneintranet.prototype#420
        recursive = True
        pworkflow = api.portal.get_tool('portal_workflow')

        def action(obj):
            transitions = pworkflow.getTransitionsFor(obj)
            if transition_id in [t['id'] for t in transitions]:
                try:
                    pworkflow.doActionFor(obj, transition_id)
                except ConflictError:
                    raise
                except Exception:
                    self.errors.append(
                        _('Could not transition: ${title}',
                          mapping={'title': safe_unicode(obj.Title())}))
                else:
                    handled.append(safe_unicode(obj.Title()))

            if recursive and IFolderish.providedBy(obj):
                for sub in obj.values():
                    action(sub)

        if transition_id:
            for uid in uids:
                obj = api.content.get(UID=uid)
                if obj:
                    action(obj)
        else:
            api.portal.show_message(
                message=_(u"Please select at workflow transition."),
                request=self.request,
                type="warning")

        if handled:
            titles = ', '.join(sorted(handled))
            msg = _(
                u"batch_change_workflow_success",
                default=u"The workflow state of the following items has been changed: ${title_elems}",  # noqa
                mapping={"title_elems": titles}
            )
            api.portal.show_message(
                message=msg,
                request=self.request,
                type="success",
            )
        else:
            api.portal.show_message(
                message=_(u"No items could be changed in their workflow states."),  # noqa
                request=self.request,
                type="info",
            )

        return self.redirect()
