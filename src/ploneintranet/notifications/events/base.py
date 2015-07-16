# -*- coding: utf-8 -*-
from ..interfaces import IMessageClassHandler
from ..interfaces import IMessageFactory
from zope.component import getAdapter
from plone import api


def base_handler(obj, event):
    ''' This is a very basic handler that creates a message
    for the event object and spreads it with a dedicated handler
    '''
    message = IMessageFactory(obj)()
    handler = getAdapter(obj, IMessageClassHandler, name=message.predicate)
    handler.add(message)


def status_update_handler(obj, event):
    if not obj.mentions:
        return
    message = IMessageFactory(obj)()
    tool = api.portal.get_tool('ploneintranet_notifications')
    for userid in obj.mentions.keys():
        queue = tool.get_user_queue(userid)
        queue.append(message.clone())
