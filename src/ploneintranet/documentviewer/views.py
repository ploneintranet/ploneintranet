# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from persistent.dict import PersistentDict
from plone.memoize.view import memoize
from zope.annotation.interfaces import IAnnotations


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
