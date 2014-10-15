# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from persistent.dict import PersistentDict
from plone import api
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

    def get_default_preview(self):
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
