# -*- coding: utf-8 -*-

from ploneintranet.messaging.interfaces import IMessageSendEvent

from zope.interface import implementer


@implementer(IMessageSendEvent)
class MessageSendEvent(object):

    def __init__(self, message):
        self.message = message
