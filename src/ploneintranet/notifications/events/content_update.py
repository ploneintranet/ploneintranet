# -*- coding: utf-8 -*-
from plone import api
from ploneintranet.notifications.message import create_message
from ploneintranet.notifications.msg_classes import fake_adapter


def create_actors(obj, event):
    member = api.user.get_current()
    actors = dict(
        fullname=member.getProperty('fullname', ''),
        userid=member.getId(),
        email=member.getProperty('email', '')
    )
    return actors


def added(obj, event):
    ''' Dexterity content is added, show it to everyone
    '''
    actors = create_actors(obj, event)
    predicate = 'GLOBAL_NOTICE'
    obj = {'id': obj.id,
           'url': obj.absolute_url(relative=True),
           'title': obj.title_or_id()}
    message = create_message(actors, predicate, obj)
    msg_class_handler = fake_adapter(predicate)
    msg_class_handler.add(message)


def changed(obj, event):
    ''' Dexterity content is updated, show it to everyone
    '''
    actors = create_actors(obj, event)
    predicate = 'GLOBAL_NOTICE'
    obj = {'id': obj.id,
           'url': obj.absolute_url(relative=True),
           'title': obj.title_or_id()}
    message = create_message(actors, predicate, obj)
    msg_class_handler = fake_adapter(predicate)
    msg_class_handler.add(message)


def workflow_change(obj, event):
    ''' Dexterity content workflow changed, show it to everyone
    '''
    actors = create_actors(obj, event)
    predicate = 'GLOBAL_NOTICE'
    obj = {'id': obj.id,
           'url': obj.absolute_url(relative=True),
           'title': obj.title_or_id()}
    message = create_message(actors, predicate, obj)
    msg_class_handler = fake_adapter(predicate)
    msg_class_handler.add(message)
