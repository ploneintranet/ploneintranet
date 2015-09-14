# -*- coding: utf-8 -*-
from .utils import dexterity_update
from Acquisition import aq_inner
# from DateTime import DateTime
from plone import api
from plone.app.blocks.interfaces import IBlocksTransformEnabled
from plone.app.event.base import default_timezone
from plone.memoize.view import memoize
from plone.rfc822.interfaces import IPrimaryFieldInfo
from ploneintranet import api as pi_api
from ploneintranet.core import ploneintranetCoreMessageFactory as _  # noqa
from ploneintranet.workspace.utils import map_content_type
from ploneintranet.workspace.utils import parent_workspace
from Products.Five import BrowserView
from zope import component
from zope.component import getUtility
from zope.event import notify
from zope.interface import implementer
from zope.lifecycleevent import ObjectModifiedEvent
from zope.schema.interfaces import IVocabularyFactory


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

    def validate(self):
        ''' Return truish if valid
        '''
        return True

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
            mod = False
            if self.validate():
                mod, errors = dexterity_update(context)
                if mod:
                    messages.append("Your changes have been saved.")
            modified = modified or mod

        if errors:
            api.portal.show_message(_(
                "There was a problem: %s" % errors), request=self.request,
                type="error")

        elif modified:
            api.portal.show_message(
                ' '.join(messages), request=self.request,
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
            # Only target states are shown in the UI. If two transitions lead
            # to the same state we want to show the state only once.
            if new_state_id not in [item['new_state_id'] for item in states]:
                title = getattr(available_states, new_state_id).title
                states.append(dict(
                    action=action['id'],
                    title=title,
                    new_state_id=new_state_id,
                    selected=None,
                ))
        return sorted(states, key=lambda x: x['title'])

    def previews(self):
        return pi_api.previews.get_preview_urls(self.context)

    def is_available(self):
        return pi_api.previews.has_previews(self.context)

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

    def content_type_name(self):
        """Gets a name for the type of the primary field of this content"""
        # Need this to be able to describe what is going to be downloaded
        # in the sharing tooltip. Cornelis seems to want to name the content
        # type in cleartext (Download as Microsoft Word) so we might will need
        # to extend this with a clear name mapper that then again might need
        # translation support. For now, return the name only.
        primary_field_info = IPrimaryFieldInfo(self.context)
        name = ''
        if hasattr(primary_field_info.value, "contentType"):
            contenttype = primary_field_info.value.contentType
            name = map_content_type(contenttype)
        if name:
            return name.capitalize()
        return "unknown"


class HelperView(BrowserView):
    ''' Use this to provide helper methods
    '''

    def get_selected_tz(self):
        ''' Let's try to get this from the start attribute (if found).
        Otherwise default to the default timezone.
        '''
        try:
            return str(self.context.start.tzinfo)
        except:
            return default_timezone()

    def get_tz_options(self):
        '''Returns the timezone options to be used in a select
        '''
        selected_tz = self.get_selected_tz()
        plone_tzs = getUtility(
            IVocabularyFactory,
            'plone.app.vocabularies.CommonTimezones'
        )(self.context)
        # The offset and daylight depends on the date/time,
        # so it is not easy to set it up coherently
        return [{
            'id': x.token,
            'gmt_adjustment': '',  # "GMT+12:00",
            'use_daylight': '',  # 0
            'selected': x.token == selected_tz and x.token or None,
            'value': x.token,
            'label': x.title,  # '(GMT+12:00) Fiji, Kamchatka, Marshall Is.'
        } for x in plone_tzs]
