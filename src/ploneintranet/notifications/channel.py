# -*- coding: utf-8 -*-
from plone import api
from ploneintranet.notifications.interfaces import IChannel
from zope.interface import implements


class AllChannel(object):
    implements(IChannel)

    def __init__(self, userid):
        self.userid = userid
        tool = api.portal.get_tool('ploneintranet_notifications')
        self.queue = tool.get_user_queue(userid)

    def get_unread_count(self):
        return len(self.get_unread_messages(keep_unread=True))

    def get_unread_messages(self, keep_unread=False):
        messages = filter(lambda msg: msg.is_unread(),
                          self.get_all_messages(keep_unread=True))

        if not keep_unread:
            for message in messages:
                message.mark_as_read()

        return messages

    def get_all_messages(self, limit=None,
                         keep_unread=False):
        if not limit:
            messages = self.queue[:]
        else:
            messages = self.queue[:limit]

        if not keep_unread:
            for message in messages:
                message.mark_as_read()

        return sorted(messages,
                      key=lambda x: x.obj['message_last_modification_date'],
                      reverse=True)
