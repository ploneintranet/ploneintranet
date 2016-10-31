# -*- coding: utf-8 -*-
from Acquisition import aq_inner

from plone import api
from ploneintranet.workspace.basecontent import baseviews


class NewsItemEdit(baseviews.ContentView):

    def sidebar(self):
        app = self.context.aq_parent
        publisher = api.content.get_view('publisher', app, self.request)
        return publisher.sidebar()

    def __call__(self):
        context = aq_inner(self.context)
        self.can_edit = api.user.has_permission('Modify portal content',
                                                obj=context)
        if self.request.method == 'POST':
            self.update()
        return super(NewsItemEdit, self).__call__()

    def update(self):
        return super(NewsItemEdit, self).update()
