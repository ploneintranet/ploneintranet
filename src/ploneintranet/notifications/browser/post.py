# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from plone import api
from plone.memoize.view import memoize
from ploneintranet.notifications.channel import AllChannel
from ploneintranet import api as pi_api


class PostView(BrowserView):

    def message(self):
        self.id = self.request.get('thread_id')
        if self.id:
            return self.get_notification_by_user_and_id(self.id)

    @memoize
    def get_notification_by_user_and_id(self, id):
        self.tool = api.portal.get_tool(name='portal_notification')
        self.user = api.user.get_current()
        channel = AllChannel(self.user.getUserId())
        messages = channel.get_all_messages(keep_unread=True)
        for message in messages:
            if message.obj['id'] == long(id):
                return message

    def get_author_image(self, member_id):
        """
        Fetch the author portrait image url accoding to member_id
        """

        return pi_api.userprofile.avatar_tag(member_id)
