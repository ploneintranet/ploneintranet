# -*- coding: utf-8 -*-

from datetime import datetime
from persistent import Persistent
from persistent.dict import PersistentDict
from persistent.list import PersistentList
from ploneintranet.notifications.interfaces import IMessage
from zope.interface import implements


class Message(Persistent):
    actors = None
    predicate = ''
    obj = {}

    implements(IMessage)

    def __init__(self, actors, predicate, obj):
        self.actors = PersistentList(map(PersistentDict, actors))

        self.predicate = predicate

        self.obj = PersistentDict(obj.copy())

        if 'url' not in obj:
            self.obj['url'] = ''
        if 'message_last_modification_date' not in obj:
            self.obj['message_last_modification_date'] = datetime.utcnow()
        if 'read' not in obj:
            self.obj['read'] = False


def create_message(actors, predicate, obj):
    return Message(actors, predicate, obj)
