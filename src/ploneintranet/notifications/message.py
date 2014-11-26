# -*- coding: utf-8 -*-

from datetime import datetime
from persistent import Persistent
from ploneintranet.notifications.interfaces import IMessage
from zope.interface import implements
import pickle


class Message(Persistent):
    actors = None
    predicate = ''
    obj = {}

    implements(IMessage)

    def __init__(self, actors, predicate, obj):
        self.actors = actors

        # make sure actors is a list
        if not isinstance(self.actors, list):
            self.actors = [self.actors]

        self.predicate = predicate

        self.obj = obj.copy()

        if 'url' not in obj:
            self.obj['url'] = ''
        if 'message_last_modification_date' not in obj:
            self.obj['message_last_modification_date'] = datetime.utcnow()
        if 'read' not in obj:
            self.obj['read'] = False

    def mark_as_read(self, now=None):
        if now is None:
            now = datetime.utcnow()
        self.obj['read'] = now
        self._p_changed = 1

    def marked_read_at(self):
        return self.obj['read']

    def is_unread(self):
        return self.marked_read_at() is False

    def update_object(self, obj):
        self.obj = obj
        self.obj['message_last_modification_date'] = datetime.utcnow()
        self._p_changed = 1

    def update_actors(self, added=[], removed=[]):
        for add in added:
            if add not in self.actors:
                self.actors.append(add)
                self._p_changed = 1
        for remove in removed:
            if remove in self.actors:
                self.actors.remove(remove)
                self._p_changed = 1

    def clone(self):
        clone = lambda x: pickle.loads(pickle.dumps(x))
        return create_message(actors=clone(self.actors),
                              predicate=self.predicate,
                              obj=clone(self.obj))


def create_message(actors, predicate, obj):
    return Message(actors, predicate, obj)
