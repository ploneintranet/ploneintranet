# -*- coding: utf-8 -*-
from zope.component import getUtility

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api as plone_api
from plone.protect import PostOnly

from ploneintranet.core import ploneintranetCoreMessageFactory as _  # noqa
from ploneintranet.network.interfaces import INetworkTool

import uuid


class NotAllowed(Exception):
    pass


class ToggleFollowUser(BrowserView):

    """View that toggles follow/unfollow on a User."""

    index = ViewPageTemplateFile('templates/toggle_follow.pt')

    def __call__(self):
        self.util = getUtility(INetworkTool)
        self.followed_id = self.context.username
        self.follow_type = 'user'
        self.follower = plone_api.user.get_current().getUserName()

        self.is_followed = self.util.is_followed(
            self.follow_type, self.followed_id, self.follower)

        if 'do_toggle_follow' in self.request:
            self.toggle_follow()

        if self.is_followed:
            self.verb = _(u'Unfollow')
        else:
            self.verb = _(u'Follow')

        self.unique_id = uuid.uuid4().hex

        return self.index()

    def toggle_follow(self):
        """Follow/unfollow context."""
        PostOnly(self.request)

        if self.is_followed:
            self.util.unfollow(
                self.follow_type, self.followed_id, self.follower)
        else:
            self.util.follow(
                self.follow_type, self.followed_id, self.follower)
        self.is_followed = not self.is_followed

    def action(self):
        return "%s/@@toggle_follow" % self.context.absolute_url()
