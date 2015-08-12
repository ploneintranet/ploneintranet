# -*- coding: utf-8 -*-
import logging

from ..interfaces import IMessageClassHandler
from ..interfaces import IMessageFactory
from zope.component import getAdapter
from plone import api

from ploneintranet.api import userprofile
from ploneintranet.gcm.interfaces import IGCMService

logger = logging.getLogger(__name__)


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
        msg = message.clone()
        queue = tool.get_user_queue(userid)
        queue.append(msg)
        user = userprofile.get(userid)
        if user is None:
            continue
        gcm_service = IGCMService(user, None)
        if gcm_service is not None:
            logger.info('Got GCM service')
            gcm_service.send_push_notification(msg)
        else:
            logger.error('No GCM service adapter for %r', user)
