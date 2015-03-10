# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Products.Five import BrowserView
from plone.protect import CheckAuthenticator, PostOnly
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


class DocumentView(BrowserView):

    def __call__(self, title=None, description=None, tags=[]):
        context = aq_inner(self.context)
        if title or description or tags:
            CheckAuthenticator(self.request)
            PostOnly(self.request)
            modified = False
            if title and title != context.title:
                context.title = title
                modified = True
            if description and description != context.description:
                context.description = description
                modified = True
            if tags and tags != context.subjects:
                context.subjects = tags
                modified = True
            if modified:
                context.reindexObject()
                notify(ObjectModifiedEvent(context))

        return super(DocumentView, self).__call__()
