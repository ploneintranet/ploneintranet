import logging
import time

from BTrees.LOBTree import LOBTree
from BTrees.OOBTree import OOBTree
from BTrees.LLBTree import LLTreeSet

from persistent import Persistent
from Acquisition import aq_base
from Acquisition import Explicit

from zope.annotation.interfaces import IAnnotations
from zope.app.container.contained import ObjectAddedEvent
from zope.app.container.contained import ObjectRemovedEvent
from zope.event import notify
from zope.interface import implements

from interfaces import IStatusContainer
from interfaces import IStatusUpdate

logger = logging.getLogger('plonesocial.microblog')

ANNOTATION_KEY = 'plonesocial.microblog'


class StatusContainer(Persistent, Explicit):

    implements(IStatusContainer)

    def __init__(self, context):
        self.context = context
        # primary storage: (long statusid) -> (object IStatusUpdate)
        self.__status_mapping = LOBTree()
        # index by user: (string userid) -> (object TreeSet(long statusid))
        self.__user_mapping = OOBTree()
        # index by tag: (string tag) -> (object TreeSet(long statusid))
        self.__tag_mapping = OOBTree()

    def _check_status(self, status):
        if not IStatusUpdate.providedBy(status):
            raise ValueError("IStatusUpdate interface not provided.")

    def add(self, status):
        self._check_status(status)
        status.id = long(time.time() * 1e6)
        # see ZODB/Btree/Interfaces.py
        # If the key was already in the collection, there is no change
        while not self.__status_mapping.insert(status.id, status):
            status.id += 1
        self._idx_user(status)
        self._idx_tag(status)
        event = ObjectAddedEvent(status,
                                 newParent=self.context, newName=status.id)
        notify(event)
        logger.info("Added StatusUpdate %s (%s: %s)",
                    status.id, status.userid, status.text)

    def _idx_user(self, status):
        userid = unicode(status.userid)
        # If the key was already in the collection, there is no change
        # create user treeset if not already present
        self.__user_mapping.insert(userid, LLTreeSet())
        # add status id to user treeset
        self.__user_mapping[userid].insert(status.id)

    def _idx_tag(self, status):
        for tag in [unicode(tag) for tag in status.tags]:
            # If the key was already in the collection, there is no change
            # create tag treeset if not already present
            self.__tag_mapping.insert(tag, LLTreeSet())
            # add status id to tag treeset
            self.__tag_mapping[tag].insert(status.id)

    def insert(self, key, status):
        """Low-level BTree compatibility method.
        Don't use this, it will destroy index consistency.
        Use .add() instead.
        """
        raise AttributeError("Unsupported method")

    def clear(self):
        self.__user_mapping.clear()
        self.__tag_mapping.clear()
        return self.__status_mapping.clear()

    def get(self, key, default=None):
        return self.__status_mapping.get(key, default=default)

    def items(self, min=None, max=None):
        return self.__status_mapping.items(min=min, max=max)

    def iteritems(self, min=None, max=None):
        return self.__status_mapping.iteritems(min=min, max=max)

    def iterkeys(self, min=None, max=None):
        return self.__status_mapping.iterkeys(min=min, max=max)

    def itervalues(self, min=None, max=None):
        return self.__status_mapping.itervalues(min=min, max=max)

    def keys(self, min=None, max=None):
        return self.__status_mapping.keys(min=min, max=max)

    def pop(self, k, d=None):
        _marker = object()
        result = self.__status_mapping.pop(k, d=_marker)
        if result is _marker:
            return d
        event = ObjectRemovedEvent(result, oldParent=self.context,
                                   oldName=k)
        notify(event)
        return result

    def setdefault(self, k, d):
        return self.__status_mapping.setdefault(k, d)

    def update(self, collection):
        return self.__status_mapping.update(collection)

    def values(self, min=None, max=None):
        return self.__status_mapping.values(min=min, max=max)


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
