# -*- coding: utf-8 -*-
from zope.component import getUtility

from Products.Five import BrowserView
from plone import api as plone_api

from ploneintranet.network.interfaces import INetworkTool


class ToggleFollow(BrowserView):

    """View that toggles follow/unfollow on a context."""

    def __init__(self, context, request):
        self.context = context  # the item being followed
        self.request = request
        self.util = getUtility(INetworkTool)
        self.followed_id = self.context.getId()
        self.follow_type = 'user'

    def __call__(self):
        current_username = plone_api.user.get_current().getUserName()
        is_followed = self.util.is_followed(
            self.follow_type, self.followed_id, current_username)
        if is_followed:
            self.util.unfollow(
                self.follow_type, self.followed_id, current_username)
        else:
            self.util.follow(
                self.follow_type, self.followed_id, current_username)
