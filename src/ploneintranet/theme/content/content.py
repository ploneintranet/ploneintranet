# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from plone import api
from plone.app.blocks.interfaces import IBlocksTransformEnabled
from plone.app.textfield.value import RichTextValue
from ploneintranet.docconv.client.interfaces import IDocconv
from ploneintranet.workspace.utils import parent_workspace
from zope.event import notify
from zope.interface import implementer
from zope.lifecycleevent import ObjectModifiedEvent

@implementer(IBlocksTransformEnabled)
class ContentView(BrowserView):
    """View and edit class/form for all default DX content-types."""

    def __call__(self, title=None, description=None, tags=[], text=None):
        """Render the default template and evaluate the form when editing."""
        context = aq_inner(self.context)
        self.workspace = parent_workspace(context)
        self.can_edit = api.user.has_permission(
            'Modify portal content',
            obj=context)
        if self.can_edit and title or description or tags or text:
            modified = False
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
                context.reindexObject()
                notify(ObjectModifiedEvent(context))

        return super(ContentView, self).__call__()

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
