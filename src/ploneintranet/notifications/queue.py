# -*- coding: utf-8 -*-

from Acquisition import Explicit
from BTrees import OOBTree
from interfaces import INotificationsQueues
from persistent import Persistent
from persistent.list import PersistentList
from zope.interface import implements
import logging
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides
from zope.globalrequest import getRequest


logger = logging.getLogger(__name__)


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

    def get_user_queue(self, userid):
        if userid not in self._users:
            request = getRequest()
            if request is not None:
                alsoProvides(request, IDisableCSRFProtection)
            self._users[userid] = PersistentList()
        return self._users[userid]

    def del_user_queue(self, userid):
        del self._users[userid]
