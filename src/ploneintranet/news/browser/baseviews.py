# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from plone import api


class NewsItemEdit(BrowserView):

    def sidebar(self):
        app = self.context.aq_parent
        publisher = api.content.get_view('publisher', app, self.request)
        return publisher.sidebar()
