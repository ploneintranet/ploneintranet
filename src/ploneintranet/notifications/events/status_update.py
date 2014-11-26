# -*- coding: utf-8 -*-
from ..message import create_message
from plone import api


def added(obj, event):
    ''' What to do when a status update is added to its container
    '''
    member = api.user.get(username=obj.creator)
    obj.creator
    actors = dict(
        fullname=member.getProperty('fullname'),
        userid=member.getId(),
        email=member.getProperty('email')
    )
    predicate = 'StatusUpdate'
    message = create_message(actors, predicate, obj.__dict__)
    pin = api.portal.get_tool('ploneintranet_notifications')
    queue = pin.get_user_queue(member)
    queue.append(message)
