import threading
import Queue
import logging
import time
import math

from BTrees import LOBTree
from BTrees import OOBTree
from BTrees import LLBTree

from persistent import Persistent
import transaction
from Acquisition import Explicit
from AccessControl import getSecurityManager
from AccessControl import Unauthorized

from zope.app.container.contained import ObjectAddedEvent
from zope.event import notify
from zope.interface import implements

from interfaces import IStatusContainer
from interfaces import IStatusUpdate
from utils import longkeysortreverse

logger = logging.getLogger('plonesocial.microblog')

LOCK = threading.RLock()
STATUSQUEUE = Queue.PriorityQueue()

# max in-memory time in millisec before disk sync
MAX_QUEUE_AGE = 1000


class BaseStatusContainer(Persistent, Explicit):

    """This implements IStatusUpdate storage, indexing and query logic.

    This is just a base class, the actual IStorageContainer used
    in the implementation is the QueuedStatusContainer defined below.

    StatusUpdates are stored in the private _status_mapping BTree.
    A subset of BTree accessors are exposed, see interfaces.py.
    StatusUpdates are keyed by longint microsecond ids.

    Additionally, StatusUpdates are indexed by users (and TODO: tags).
    These indexes use the same longint microsecond IStatusUpdate.id.

    Special user_* prefixed accessors take an extra argument 'users',
    an interable of userids, and return IStatusUpdate keys, instances or items
    filtered by userids, in addition to the normal min/max statusid filters.
    """

    implements(IStatusContainer)

    def __init__(self, context=None):
        self._mtime = 0
        # primary storage: (long statusid) -> (object IStatusUpdate)
        self._status_mapping = LOBTree.LOBTree()
        # index by user: (string userid) -> (object TreeSet(long statusid))
        self._user_mapping = OOBTree.OOBTree()
        # index by tag: (string tag) -> (object TreeSet(long statusid))
        self._tag_mapping = OOBTree.OOBTree()

    def add(self, status):
        self._check_permission("add")
        self._check_status(status)
        self._store(status)

    def _store(self, status):
        # see ZODB/Btree/Interfaces.py
        # If the key was already in the collection, there is no change
        while not self._status_mapping.insert(status.id, status):
            status.id += 1
        self._idx_user(status)
        self._idx_tag(status)
        self._notify(status)

    def _check_status(self, status):
        if not IStatusUpdate.providedBy(status):
            raise ValueError("IStatusUpdate interface not provided.")

    def _check_permission(self, perm="read"):
        if perm == "read":
            permission = "Plone Social: View Microblog Status Update"
        else:
            permission = "Plone Social: Add Microblog Status Update"
        if not getSecurityManager().checkPermission(permission, self):
            raise Unauthorized("You do not have permission <%s>" % permission)

    def _notify(self, status):
        event = ObjectAddedEvent(status,
                                 newParent=self,
                                 newName=status.id)
        notify(event)
#        logger.info("Added StatusUpdate %s (%s: %s)",
#                    status.id, status.userid, status.text)

    def _idx_user(self, status):
        userid = unicode(status.userid)
        # If the key was already in the collection, there is no change
        # create user treeset if not already present
        self._user_mapping.insert(userid, LLBTree.LLTreeSet())
        # add status id to user treeset
        self._user_mapping[userid].insert(status.id)

    def _idx_tag(self, status):
        for tag in [unicode(tag) for tag in status.tags]:
            # If the key was already in the collection, there is no change
            # create tag treeset if not already present
            self._tag_mapping.insert(tag, LLBTree.LLTreeSet())
            # add status id to tag treeset
            self._tag_mapping[tag].insert(status.id)

    def clear(self):
        self._user_mapping.clear()
        self._tag_mapping.clear()
        return self._status_mapping.clear()

    ## blocked IBTree methods to protect index consistency
    ## (also not sensible for our use case)

    def insert(self, key, value):
        raise NotImplementedError("Can't allow that to happen.")

    def pop(self, k, d=None):
        raise NotImplementedError("Can't allow that to happen.")

    def setdefault(self, k, d):
        raise NotImplementedError("Can't allow that to happen.")

    def update(self, collection):
        raise NotImplementedError("Can't allow that to happen.")

    ## primary accessors

    def get(self, key):
        self._check_permission("read")
        return self._status_mapping.get(key)

    def items(self, min=None, max=None, limit=100, tag=None):
        return ((key, self.get(key))
                for key in self.keys(min, max, limit, tag))

    def keys(self, min=None, max=None, limit=100, tag=None):
        self._check_permission("read")
        if tag:
            if tag not in self._tag_mapping:
                return ()
            mapping = LLBTree.intersection(
                LLBTree.LLTreeSet(self._status_mapping.keys()),
                self._tag_mapping[tag])
        else:
            mapping = self._status_mapping
        return longkeysortreverse(mapping,
                                  min, max, limit)

    def values(self, min=None, max=None, limit=100, tag=None):
        return (self.get(key)
                for key in self.keys(min, max, limit, tag))

    iteritems = items
    iterkeys = keys
    itervalues = values

    ## user accessors

    # no user_get

    def user_items(self, users, min=None, max=None, limit=100, tag=None):
        return ((key, self.get(key)) for key
                in self.user_keys(users, min, max, limit, tag))

    def user_keys(self, users, min=None, max=None, limit=100, tag=None):
        if not users:
            return ()

        if users == str(users):
            # single user optimization
            userid = users
            mapping = self._user_mapping.get(userid)
            if not mapping:
                return ()

        else:
            # collection of user LLTreeSet
            treesets = (self._user_mapping.get(userid)
                        for userid in users
                        if userid in self._user_mapping.keys())
            mapping = reduce(LLBTree.union, treesets, LLBTree.TreeSet())

        if tag:
            if tag not in self._tag_mapping:
                return ()
            mapping = LLBTree.intersection(mapping,
                                           self._tag_mapping[tag])

        return longkeysortreverse(mapping,
                                  min, max, limit)

    def user_values(self, users, min=None, max=None, limit=100, tag=None):
        return (self.get(key) for key
                in self.user_keys(users, min, max, limit, tag))

    user_iteritems = user_items
    user_iterkeys = user_keys
    user_itervalues = user_values


class QueuedStatusContainer(BaseStatusContainer):

    """A write performance optimized IStatusContainer.

    This separates the queuing logic from the base class to make
    the code more readable (and testable).

    For performance reasons, an in-memory STATUSQUEUE is used.
    StatusContainer.add() puts StatusUpdates into the queue.

    MAX_QUEUE_AGE is the commit window in milliseconds.
    To disable batch queuing, set MAX_QUEUE_AGE = 0

    .add() calls .autoflush(), which flushes the queue when
    ._mtime is longer than MAX_QUEUE_AGE ago.

    So each .add() checks the queue. In a low-traffic site this will
    result in immediate disk writes (msg frequency < timeout).
    In a high-traffic site this will result on one write per timeout,
    which makes it possible to attain > 100 status update inserts
    per second.

    Note that the algorithm is structured in such a way, that the
    system automatically adapts to low/high traffic conditions.

    Additionally, a non-interactive queue flush is set up via
    _schedule_flush() which uses a volatile thread timer _v_timer
    to set up a non-interactive queue flush. This ensures that
    the "last Tweet of the day" also gets committed to disk.

    An attempt is made to make self._mtime and self._v_timer
    thread-safe. These function as a kind of ad-hoc locking
    mechanism so that only one thread at a time is flushing the
    memory queue into persistent storage.
    """

    implements(IStatusContainer)

    def add(self, status):
        self._check_permission("add")
        self._check_status(status)
        if MAX_QUEUE_AGE > 0:
            self._queue(status)
            # fallback sync in case of NO traffic (kernel timer)
            self._schedule_flush()
            # immediate sync on low traffic (old ._mtime)
            # postpones sync on high traffic (next .add())
            return self._autoflush()
        else:
            self._store(status)
            return 1  # immediate write

    def _queue(self, status):
        STATUSQUEUE.put((status.id, status))

    def _schedule_flush(self):
        """A fallback queue flusher that runs without user interactions"""
        if not MAX_QUEUE_AGE > 0:
            return

        try:
            # non-persisted, absent on first request
            self._v_timer
        except AttributeError:
            # initialize on first request
            self._v_timer = None

        if self._v_timer is not None:
            # timer already running
            return

        # only a one-second granularity, round upwards
        timeout = int(math.ceil(float(MAX_QUEUE_AGE) / 1000))
        with LOCK:
            #logger.info("Setting timer")
            self._v_timer = threading.Timer(timeout,
                                            self._scheduled_autoflush)
            self._v_timer.start()

    def _scheduled_autoflush(self):
        """This method is run from the timer, outside a normal request scope.
        This requires an explicit commit on db write"""
        if self._autoflush():  # returns 1 on actual write
            transaction.commit()

    def _autoflush(self):
        #logger.info("autoflush")
        if int(time.time() * 1000) - self._mtime > MAX_QUEUE_AGE:
            return self.flush_queue()  # 1 on write, 0 on noop
        return 0  # no write

    def flush_queue(self):
        #logger.info("flush_queue")

        with LOCK:
            # block autoflush
            self._mtime = int(time.time() * 1000)
            # cancel scheduled flush
            if self._v_timer is not None:
                #logger.info("Cancelling timer")
                self._v_timer.cancel()
                self._v_timer = None

        if STATUSQUEUE.empty():
            return 0  # no write

        while True:
            try:
                (id, status) = STATUSQUEUE.get(block=False)
                self._store(status)
            except Queue.Empty:
                break
        return 1  # confirmed write
