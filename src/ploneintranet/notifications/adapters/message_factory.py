# -*- coding: utf-8 -*-
from plone import api


class Base(object):
    ''' A base adapter for creating a notification
    '''
    def __init__(self, context):
        ''' Initializes this adapter
        '''

    def get_actors(self, event):
        ''' Gets the list of actors bound to this notification
        '''
        member = api.user.get_current()
        actors = dict(
            fullname=member.getProperty('fullname', ''),
            userid=member.getId(),
            email=member.getProperty('email', '')
        )
        return actors
