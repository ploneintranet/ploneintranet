# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Products.Five import BrowserView
from plone import api
from plone.app.blocks.interfaces import IBlocksTransformEnabled
from plone.rfc822.interfaces import IPrimaryFieldInfo
from plone.memoize.view import memoize
from ploneintranet.docconv.client.interfaces import IDocconv
from ploneintranet.workspace.utils import parent_workspace
from ploneintranet.workspace.utils import map_content_type
from zope import component
from zope.event import notify
from zope.interface import implementer
from zope.lifecycleevent import ObjectModifiedEvent
from ploneintranet.theme import _
from .utils import dexterity_update


@implementer(IBlocksTransformEnabled)
class ContentView(BrowserView):
    """View and edit class/form for all default DX content-types."""

    def __call__(self, title=None, description=None, tags=[], text=None):
        """Render the default template and evaluate the form when editing."""
        context = aq_inner(self.context)
        self.workspace = parent_workspace(context)
        self.can_edit = api.user.has_permission(
            'Modify portal content',
            obj=context
        )
        # When saving, force to POST
        if self.request.method == 'POST':
            self.update()

        return super(ContentView, self).__call__()

    def update(self):
        """ """
        context = aq_inner(self.context)
        modified = False
        errors = None
        messages = []

        if (
                self.request.get('workflow_action') and
                not self.request.get('form.submitted')):
            api.content.transition(
                obj=context,
                transition=self.request.get('workflow_action')
            )
            # re-calculate can_edit after the workflow state change
            self.can_edit = api.user.has_permission(
                'Modify portal content',
                obj=context
            )
            modified = True
            messages.append("The workflow state has been changed.")

        if self.can_edit:
            mod, errors = dexterity_update(context)
            if mod:
                messages.append("Your changes have been saved.")
            modified = modified or mod

        if errors:
            api.portal.show_message(_(
                "There was a problem: %s" % errors), request=self.request,
                type="error")

        elif modified:
            api.portal.show_message(_(
                ' '.join(messages)), request=self.request,
                type="success")
            context.reindexObject()
            notify(ObjectModifiedEvent(context))

    @property
    @memoize
    def wf_tool(self):
        return api.portal.get_tool('portal_workflow')

    @memoize
    def _get_active_workflows(self):
        return self.wf_tool.getWorkflowsFor(aq_inner(self.context))

    def has_workflow(self):
        return len(self._get_active_workflows()) > 0

    def get_workflow_state(self):
        return api.content.get_state(obj=aq_inner(self.context))

    def get_workflow_transitions(self):
        """
            Return possible workflow transitions and destination state names
        """
        context = aq_inner(self.context)
        # This check for locked state was copied from star - unclear if needed
        locking_info = component.queryMultiAdapter(
            (context, self.request), name='plone_lock_info')
        if locking_info and locking_info.is_locked_for_current_user():
            return []

        current_state_id = api.content.get_state(obj=aq_inner(self.context))

        if current_state_id is None:
            return []

        available_states = self._get_active_workflows()[0].states

        current_state = getattr(available_states, current_state_id).title
        states = [dict(
            action='',
            title=current_state or current_state_id,
            new_state_id='',
            selected='selected')]

        workflow_actions = self.wf_tool.listActionInfos(object=context)
        for action in workflow_actions:
            if action['category'] != 'workflow':
                continue
            new_state_id = action['transition'].new_state_id
            title = getattr(available_states, new_state_id).title
            states.append(dict(
                action=action['id'],
                title=title,
                new_state_id=new_state_id,
                selected=None,
            ))
        # Todo: enforce a given order?
        return states

    def number_of_file_previews(self):
        """The number of previews generated for a file."""
        context = aq_inner(self.context)
        if context.portal_type != 'File':
            return
        try:
            docconv = IDocconv(self.context)
        except TypeError:  # TODO: prevent this form happening in tests
            return
        if docconv.has_previews():
            return docconv.get_number_of_pages()

    def image_url(self):
        """The img-url used to construct the img-tag."""
        context = aq_inner(self.context)
        if getattr(context, 'image', None) is not None:
            return '{}/@@images/image'.format(context.absolute_url())

    def icon_class(self):
        """Gets the icon class for the primary field of this content"""
        primary_field_info = IPrimaryFieldInfo(self.context)
        if hasattr(primary_field_info.value, "contentType"):
            contenttype = primary_field_info.value.contentType
            icon_name = map_content_type(contenttype)
            if icon_name:
                return 'icon-file-{0}'.format(icon_name)
        return 'icon-file-code'
