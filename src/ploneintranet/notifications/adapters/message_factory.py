# -*- coding: utf-8 -*-
from plone import api
from ploneintranet.notifications.message import Message


class Base(object):
    ''' A base adapter for creating a notification
    '''
    predicate = 'GLOBAL_NOTICE'

    def __init__(self, context):
        ''' Initializes this adapter
        '''
        self.context = context

    def get_actors(self):
        ''' Get the creators of the object as plone users
        '''
        user = api.user.get_current()
        actors = [{
            'fullname': user.getProperty('fullname', ''),
            'userid': user.getId(),
            'email': user.getProperty('email', '')
        }]
        return actors

    def get_object_as_dict(self):
        ''' return a dict representation of the object
        '''
        return {
            'id': self.context.id,
            'url': self.context.absolute_url(relative=True),
            'title': self.context.title_or_id()
        }

    def __call__(self):
        ''' Create a new message
        '''
        obj = self.get_object_as_dict()
        actors = self.get_actors()
        predicate = self.predicate
        message = Message(actors, predicate, obj)
        return message


class StatusUpdate(Base):
    ''' Customize the Message factory adapter for a microblog status update
    '''
    predicate = 'STATUS_UPDATE'

    def get_object_as_dict(self):
        ''' return a dict representation of the object
        '''
        portal_relative_url = api.portal.get().absolute_url(relative=True)
        return {
            'id': self.context.id,
            'url': portal_relative_url + '/@@stream/network',
            'title': self.context.text
        }
