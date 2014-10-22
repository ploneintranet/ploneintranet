# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from plone import api
from plone.memoize.view import memoize
from ploneintranet.docconv.client import IDocconv
from zope.interface import implementer
from zope.publisher.interfaces import NotFound
from .interfaces import IDocumentviewer


@implementer(IDocumentviewer)
class Documentpreview(BrowserView):
    ''' View to get a thumbnail for a document
    '''
    thumbnail_storage_key = 'ploneintranet.thumbnails'

    @property
    @memoize
    def docconv(self):
        ''' This will take adapter for IDocconv

        '''
        return IDocconv(self.context)

    @memoize
    def has_preview(self):
        ''' Check if we have a preview
        '''
        return self.docconv.has_thumbs()

    @memoize
    def get_preview(self):
        ''' Get a preview
        '''
        if not self.has_preview():
            return None
        thumbs = self.docconv.get_thumbs()
        if not thumbs:
            return None
        # Return the image field wrapped to the context
        return thumbs[0].get(self.context)

    def get_default_preview_url(self):
        ''' Return
        '''
        navigation_root_url = api.content.get_view(
            'plone_portal_state',
            self.context,
            self.request
        ).navigation_root_url()
        mt = api.portal.get_tool('mimetypes_registry')
        ct = getattr(self.context, 'content_type')
        for mtobj in mt.lookup(ct):
            return '%s/%s' % (navigation_root_url, mtobj.icon_path)
        return '%s/document.png' % navigation_root_url

    def is_preview_generation_queued(self):
        ''' Check if the preview generation is in some queue
        '''

    def queue_preview_generation(self):
        ''' Append preview generation for this context
        '''

    def get_preview_url(self):
        ''' Get's the preview from the storage
        If preview is not found return the default one
        '''
        # BBB this is just an example
        if self.has_preview():
            return '%s/@@document_preview/get_preview_image' % self.context.absolute_url()  # noqa
        # if preview is not found we will ask for one and return a default
        self.queue_preview_generation()  # BBB probably remove this
        return self.get_default_preview_url()

    def get_preview_image(self):
        ''' Get's the preview from the storage
        If preview is not found return the default one
        '''
        if not self.has_preview():
            raise NotFound(self, self.__name__, self.request)
        # BBB reuse ploneintranet.docconv.client view
        from ploneintranet.docconv.client.view import ThumbnailView
        return self.request.response.redirect(
            '%s/%s' % (
                self.context.absolute_url(),
                getattr(ThumbnailView, 'grokcore.component.directive.name')
            )
        )
