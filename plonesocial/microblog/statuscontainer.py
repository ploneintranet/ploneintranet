import logging
import time

from BTrees import LOBTree
from BTrees import OOBTree
from BTrees import LLBTree

from persistent import Persistent
from Acquisition import aq_base
from Acquisition import Explicit

from zope.annotation.interfaces import IAnnotations
from zope.app.container.contained import ObjectAddedEvent
from zope.event import notify
from zope.interface import implements

from interfaces import IStatusContainer
from interfaces import IStatusUpdate

logger = logging.getLogger('plonesocial.microblog')

ANNOTATION_KEY = 'plonesocial.microblog:statuscontainer'


class StatusContainer(Persistent, Explicit):

    implements(IStatusContainer)

    def __init__(self, context):
        self.context = context
        # primary storage: (long statusid) -> (object IStatusUpdate)
        self._status_mapping = LOBTree.LOBTree()
        # index by user: (string userid) -> (object TreeSet(long statusid))
        self._user_mapping = OOBTree.OOBTree()
        # index by tag: (string tag) -> (object TreeSet(long statusid))
        self._tag_mapping = OOBTree.OOBTree()

    def _check_status(self, status):
        if not IStatusUpdate.providedBy(status):
            raise ValueError("IStatusUpdate interface not provided.")

    def add(self, status):
        self._check_status(status)
        status.id = long(time.time() * 1e6)
        # see ZODB/Btree/Interfaces.py
        # If the key was already in the collection, there is no change
        while not self._status_mapping.insert(status.id, status):
            status.id += 1
        self._idx_user(status)
        self._idx_tag(status)
        self._notify(status)

    def _notify(self, status):
        event = ObjectAddedEvent(status,
                                 newParent=self.context, newName=status.id)
        notify(event)
        logger.info("Added StatusUpdate %s (%s: %s)",
                    status.id, status.userid, status.text)

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
        return self._status_mapping.get(key)

    def items(self, min=None, max=None):
        return self._status_mapping.items(min=min, max=max)

    def keys(self, min=None, max=None):
        return self._status_mapping.keys(min=min, max=max)

    def values(self, min=None, max=None):
        return self._status_mapping.values(min=min, max=max)

    def iteritems(self, min=None, max=None):
        return self._status_mapping.iteritems(min=min, max=max)

    def iterkeys(self, min=None, max=None):
        return self._status_mapping.iterkeys(min=min, max=max)

    def itervalues(self, min=None, max=None):
        return self._status_mapping.itervalues(min=min, max=max)

    ## user accessors

    # no user_get

    def user_items(self, users, min=None, max=None):
        return ((key, self.get(key)) for key
                in self.user_keys(users, min, max))

    def user_keys(self, users, min=None, max=None):
        if not users:
            return ()
        if type(users) == type('string'):
            users = [users]

        # collection of user LLTreeSet
        treesets = (self._user_mapping.get(userid) for userid in users
                    if userid in self._user_mapping.keys())
        merged = reduce(LLBTree.union, treesets, LLBTree.TreeSet())
        # list of longints is cheapest place to slice and sort
        keys = [x for x in merged.keys()
                if (not min or min <= x)
                and (not max or max >= x)]
        keys.sort()
        return keys

    def user_values(self, users, min=None, max=None):
        return (self.get(key) for key
                in self.user_keys(users, min, max))

    user_iteritems = user_items
    user_iterkeys = user_keys
    user_itervalues = user_values


def statusContainerAdapterFactory(context):
    """
    Adapter factory to store and fetch the status container from annotations.
    """
    annotions = IAnnotations(context)
    if not ANNOTATION_KEY in annotions:
        statuscontainer = StatusContainer(context)
        statuscontainer.__parent__ = aq_base(context)
        annotions[ANNOTATION_KEY] = aq_base(statuscontainer)
    else:
        statuscontainer = annotions[ANNOTATION_KEY]
    return statuscontainer.__of__(context)
