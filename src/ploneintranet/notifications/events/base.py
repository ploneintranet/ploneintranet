# -*- coding: utf-8 -*-
from ..interfaces import IMessageClassHandler
from ..interfaces import IMessageFactory
from zope.component import getAdapter


def base_handler(obj, event):
    ''' This is a very basic handler that creates a message
    for the event object and spreads it with a dedicated handler
    '''
    message = IMessageFactory(obj)()
    handler = getAdapter(obj, IMessageClassHandler, name=message.predicate)
    handler.add(message)
