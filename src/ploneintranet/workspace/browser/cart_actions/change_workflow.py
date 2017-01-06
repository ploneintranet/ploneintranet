# -*- coding: utf-8 -*-
"""A Cart Action for changing the workflow state of all items listed in cart"""

from plone import api
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.workspace.browser.cart_actions.base import BaseCartView
from Products.CMFCore.interfaces._content import IFolderish
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from urllib import urlencode
from ZODB.POSException import ConflictError


class ChangeWorkflowView(BaseCartView):
    """Change Workflow Action implementation"""

    def confirm(self):
        index = ViewPageTemplateFile("templates/change_workflow_confirmation.pt")  # noqa
        return index(self)

    def get_transitions(self):
        transitions = []
        pworkflow = api.portal.get_tool('portal_workflow')
        for obj in self.items:
            for transition in pworkflow.getTransitionsFor(obj):
                tdata = {
                    'id': transition['id'],
                    'title': transition['name']
                }
                if tdata not in transitions:
                    transitions.append(tdata)
        return transitions

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

        recursive = bool(self.request.form.get('recursive', ''))
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

        params = {
            'groupname': self.request.get('groupname', ''),
        }
        self.request.response.redirect(
            '{0}?{1}'.format(
                self.context.absolute_url(), urlencode(params)))
