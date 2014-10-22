# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from persistent.dict import PersistentDict
from plone import api
from plone.memoize.view import memoize
from zope.annotation.interfaces import IAnnotations
from zope.interface import implementer
from .interfaces import IDocumentviewer


@implementer(IDocumentviewer)
class Documentpreview(BrowserView):
    ''' View to get a thumbnail for a document
    '''
    thumbnail_storage_key = 'ploneintranet.thumbnails'

    @property
    @memoize
    def thumbnail_storage(self):
        ''' This will take the context and return the thumbnail storage
        from the annotations

        '''
        annotations = IAnnotations(self.context)
        if not self.thumbnail_storage_key in annotations:
            # BBB this is bad because will write data in the annotations
            annotations[self.thumbnail_storage_key] = PersistentDict()
        return annotations[self.thumbnail_storage_key]

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
        preview = self.context.restrictedTraverse('image_preview', None)
        if preview is not None:
            return preview.absolute_url()
        # if preview is not found we will ask for one and return a default
        self.queue_preview_generation()
        return self.get_default_preview_url()
