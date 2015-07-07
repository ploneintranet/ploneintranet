# -*- coding: utf-8 -*-
from plone import api as plone_api
from ploneintranet.notifications.interfaces import IMessageFactory


def create(userids, obj):
    """Notify one or more users

    :param userids: [required] Userids to notify
    :type userids: list
    :param obj: The item of content to notify the users about.
        (Should be adaptable to
         `ploneintranet.notifications.interfaces.IMessageFactory`)
    :type obj: object
    """
    message = IMessageFactory(obj)()
    tool = plone_api.portal.get_tool('ploneintranet_notifications')
    for userid in userids:
        queue = tool.get_user_queue(userid)
        queue.append(message.clone())
