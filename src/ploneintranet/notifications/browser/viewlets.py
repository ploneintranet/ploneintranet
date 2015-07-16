# -*- coding: utf-8 -*-
from plone import api
from plone.app.layout.viewlets import common as base
from plone.memoize.view import memoize
from ploneintranet.notifications.channel import AllChannel


class NotificationsViewlet(base.ViewletBase):
    """
    """

    @memoize
    def getNumber(self):
        user = api.user.get_current()
        # TODO a zope user like admin will fail from here
        try:
            channel = AllChannel(user.getUserId())
            count = channel.get_unread_count()
        except AttributeError:
            # AttributeError: getUserId
            count = 0
        return count
