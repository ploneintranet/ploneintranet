# -*- coding: utf-8 -*-
import logging

from ..interfaces import IMessageClassHandler
from ..interfaces import IMessageFactory
from zope.component import getAdapter, getUtility
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
    gcm_service = getUtility(IGCMService)
    gcm_reg_ids = []
    for userid in obj.mentions.keys():
        msg = message.clone()
        queue = tool.get_user_queue(userid)
        queue.append(msg)
        profile = userprofile.get(userid)
        if profile is not None:
            gcm_reg_id = profile.gcm_reg_id
            if gcm_reg_id:
                gcm_reg_ids.append(profile.gcm_reg_id)
    if gcm_reg_ids:
        gcm_service.send_push_notifications(message, to=gcm_reg_ids)
