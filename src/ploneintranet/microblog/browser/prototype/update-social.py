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
