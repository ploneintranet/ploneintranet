# -*- coding: utf-8 -*-
from plone import api
from ploneintranet.notifications.interfaces import IChannel
from zope.interface import implements


class AllChannel(object):
    implements(IChannel)

    def __init__(self, user):
        self.user = user
        tool = api.portal.get_tool('ploneintranet_notifications')
        self.queue = tool.get_user_queue(user)

    def get_unread_count(self):
        return len(self.get_unread_messages(keep_unread=True))

    def get_unread_messages(self, limit=None, keep_unread=False):
        messages = filter(lambda msg: msg.is_unread(), self.queue)
        if limit:
            messages = messages[:limit]

        if not keep_unread:
            for message in messages:
                message.mark_as_read()

        return messages

    def get_all_messages(self):
        return self.queue[:]
