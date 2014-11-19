import logging

from BTrees import OOBTree
from persistent import Persistent
from Acquisition import Explicit

from zope.interface import implements

from interfaces import INotificationsQueue

logger = logging.getLogger(__name__)


class Queue(Persistent, Explicit):
    """
    Stores queues for each user.
    Users are referenced as string userids.

    Return values are BTrees.OOBTree.OOTreeSet iterables.
    """

    implements(INotificationsQueue)

    def __init__(self, context=None):
        self._users = OOBTree.OOBTree()

    def clear(self):
        self._users = OOBTree.OOBTree()
