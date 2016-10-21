# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from ploneintranet import api as pi_api


class PostView(BrowserView):

    def statusupdate(self):
        self.id = self.request.get('thread_id')
        if self.id:
            return pi_api.microblog.statusupdate.get(long(self.id))
