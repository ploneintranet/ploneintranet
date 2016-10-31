# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from plone import api
from ploneintranet.workspace.basecontent import baseviews


class NewsItemEdit(baseviews.ContentView):

    def sidebar(self):
        app = self.context.aq_parent
        publisher = api.content.get_view('publisher', app, self.request)
        return publisher.sidebar()

    def can_review(self):
        return api.user.has_permission('Review portal content',
                                       obj=aq_inner(self.context))
