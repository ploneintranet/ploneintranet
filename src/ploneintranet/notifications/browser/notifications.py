# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from plone import api
from plone.memoize.view import memoize
from ploneintranet.notifications.channel import AllChannel


class NotificationsView(BrowserView):

    @memoize
    def your_notifications(self):
        # count to show unread messages
        display_message = []
        user = api.user.get_current()
        # TODO a zope user like admin will fail from here
        try:
            channel = AllChannel(user)
            # TODO for now we keep the everything unread keep_unread=True
            display_message = channel.get_unread_messages(keep_unread=True)
        except AttributeError:
            #AttributeError: getUserId
            display_message = []
        return display_message

    def get_author_image(self, member_id):
        """
        Fetch the author portrait image url accoding to member_id
        """
        mtool = api.portal.get_tool(name='portal_membership')
        return mtool.getPersonalPortrait(id=member_id)
