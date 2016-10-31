# -*- coding: utf-8 -*-
from Acquisition import Explicit
from BTrees import OOBTree
from BTrees.LOBTree import LOBTree
from interfaces import INotificationsQueues
from persistent import Persistent
from zope.interface import implements
import logging
import time


logger = logging.getLogger(__name__)


class AppendableLOBTree(LOBTree):
    ''' Implement append to LOBtrees to make it work like lists
    '''
    def append(self, value):
        ''' We append to the LOBtree value generating a key based on the
        current time
        '''
        key = long(time.time() * 1.e6)
        while key in self:
            key = key + 1
        self[key] = value

    def as_tuple(self, limit=None):
        ''' Return the values as a tuple.
        '''
        keys = sorted(self)
        if limit is not None:
            keys = keys[:limit]
        return tuple(self[key] for key in keys)


class Queues(Persistent, Explicit):
    """
    Stores queues for each user.
    Users are referenced as string userids.

    Return values are BTrees.OOBTree.OOTreeSet iterables.
    """

    implements(INotificationsQueues)

    def __init__(self, context=None):
        self._users = OOBTree.OOBTree()

    def clear(self):
        self._users = OOBTree.OOBTree()

    def append_to_user_queue(self, userid, value):
        if userid not in self._users:
            self._users[userid] = AppendableLOBTree()
        self._users[userid].append(value)

    def get_user_queue(self, userid, limit=None):
        if userid not in self._users:
            return ()
        return self._users[userid].as_tuple(limit)

    def del_user_queue(self, userid):
        del self._users[userid]
