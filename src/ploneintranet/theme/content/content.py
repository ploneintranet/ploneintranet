# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from plone import api
from plone.app.blocks.interfaces import IBlocksTransformEnabled
from plone.app.textfield.value import RichTextValue
from plone.memoize.view import memoize
from ploneintranet.docconv.client.interfaces import IDocconv
from ploneintranet.workspace.utils import parent_workspace
from zope.event import notify
from zope.interface import implementer
from zope.lifecycleevent import ObjectModifiedEvent
from ploneintranet.theme import _


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
        self.update(title, description, tags, text)
        return super(ContentView, self).__call__()

    def update(self, title=None, description=None, tags=[], text=None):
        """ """
        context = aq_inner(self.context)
        if not self.can_edit:
            return
        modified = False
        if self.request.get('workflow_action'):
            # TODO: should we trigger any events or reindex?
            api.content.transition(
                obj=context,
                transition=self.request.get('workflow_action')
            )
        if title or description or tags or text:
            if title and safe_unicode(title) != context.title:
                context.title = safe_unicode(title)
                modified = True
            if text:
                richtext = RichTextValue(raw=text, mimeType='text/html',
                                         outputMimeType='text/x-html-safe')
                context.text = richtext
                modified = True
            if description:
                if safe_unicode(description) != context.description:
                    context.description = safe_unicode(description)
                    modified = True
            if tags:
                tags = tuple([safe_unicode(tag) for tag in tags.split(',')])
                if tags != context.subject:
                    context.subject = tags
                    modified = True
            if modified:
                IStatusMessage(self.request).add(_(
                    "Your changes have been saved"))
                context.reindexObject()
                notify(ObjectModifiedEvent(context))

    @property
    @memoize
    def wf_tool(self):
        return api.portal.get_tool('portal_workflow')

    def has_workflow(self):
        return len(self.wf_tool.getWorkflowsFor(aq_inner(self.context))) > 0

    def get_workflow_state(self):
        return api.content.get_state(obj=aq_inner(self.context))

    def get_workflow_transitions(self):
        context = aq_inner(self.context)
        return self.wf_tool.getTransitionsFor(context)

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
