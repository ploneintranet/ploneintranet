# coding=utf-8
import logging
from Products.Five.browser import BrowserView
from plone import api

from ploneintranet.microblog.browser.tiles.newpostbox import AbstractNewPostBox

logger = logging.getLogger(__name__)


class UpdateSocialView(AbstractNewPostBox, BrowserView):
    ''' Create a new post or reply.
    '''

    def portal_url(self):
        return api.portal.get().absolute_url()

    def form_action(self):
        if self.post_context:
            _base = self.post_context.absolute_url()
        else:
            _base = self.portal_url()
        if self.thread_id:
            _action = '%s/comment-well-said.html'
        else:
            _action = '%s/post-well-done.html'
        return _action % _base
