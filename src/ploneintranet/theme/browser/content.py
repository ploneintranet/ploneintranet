# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from plone import api
from plone.app.blocks.interfaces import IBlocksTransformEnabled
from plone.protect import CheckAuthenticator, PostOnly
from ploneintranet.workspace.utils import parent_workspace
from zope.event import notify
from zope.interface import implementer
from zope.lifecycleevent import ObjectModifiedEvent


@implementer(IBlocksTransformEnabled)
class ContentView(BrowserView):
    """View and edit class/form for all default DX content-types"""

    def __call__(self, title=None, description=None, tags=[]):
        context = aq_inner(self.context)
        if title or description or tags:
            PostOnly(self.request)
            modified = False
            if title and title != context.title:
                context.title = safe_unicode(title)
                modified = True
            if description and description != context.description:
                context.description = safe_unicode(description)
                modified = True
            if tags:
                tags = tuple([safe_unicode(tag) for tag in tags.split(',')])
                context.subject = tags
                modified = True
            if modified:
                context.reindexObject()
                notify(ObjectModifiedEvent(context))

        return super(ContentView, self).__call__()

    def workspace(self):
        return parent_workspace(self)

    def file_previews(self):
        context = aq_inner(self.context)
        if context.portal_type != 'File':
            return
        return "get the damn previews!"

    def image_preview(self):
        context = aq_inner(self.context)
        images_view = api.content.get_view('images', context, self.request)
        scale = images_view.scale(fieldname='image', scale='large')
        if scale:
            return scale.tag()
