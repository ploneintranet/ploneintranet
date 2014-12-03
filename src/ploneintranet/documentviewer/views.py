# -*- coding: utf-8 -*-
from .interfaces import IDocumentviewer
from Products.Five.browser import BrowserView
from plone import api
from plone.dexterity.content import Item
from plone.memoize.view import memoize
from plone.rfc822.interfaces import IPrimaryFieldInfo
from ploneintranet.docconv.client.interfaces import IDocconv
from zope.interface import implementer
from zope.publisher.interfaces import NotFound


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

    @property
    @memoize
    def navigation_root_url(self):
        ''' Return the navigation_root_url
        '''
        return api.content.get_view(
            'plone_portal_state',
            self.context,
            self.request
        ).navigation_root_url()

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
        ''' Return the default icon for a content
        '''
        # if we are a dexterity item use the dedicated helper view
        if isinstance(self.context, Item):
            try:
                field = IPrimaryFieldInfo(self.context)
            except TypeError:
                # We don't have a primary field defined
                field = None
            if field:
                contenttype_utils = api.content.get_view(
                    'contenttype_utils',
                    self.context,
                    self.request
                )
                icon = contenttype_utils.getMimeTypeIcon(getattr(self.context, field.fieldname, None))  # noqa
                if icon.startswith(self.navigation_root_url):
                    return icon
                else:
                    return '%s/%s' % (self.navigation_root_url, icon)

        # if we are not a dexterity item try another approach
        mt = api.portal.get_tool('mimetypes_registry')
        ct = getattr(self.context, 'content_type')
        if callable(ct):
            ct = ct() or 'application/octet-stream'
        for mtobj in mt.lookup(ct):
            return '%s/%s' % (self.navigation_root_url, mtobj.icon_path)
        return '%s/document.png' % self.navigation_root_url

    def get_preview_url(self):
        ''' Get's the preview from the storage
        If preview is not found return the default one
        '''
        if self.has_preview():
            return '%s/@@document_preview/get_preview_image' % self.context.absolute_url()  # noqa
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
