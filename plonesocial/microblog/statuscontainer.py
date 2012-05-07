import logging

from BTrees.OOBTree import OOBTree
from DateTime import DateTime
from persistent import Persistent
from zope.annotation.interfaces import IAnnotations
from zope.app.container.contained import ObjectAddedEvent
from zope.app.container.contained import ObjectRemovedEvent
from zope.event import notify
from zope.interface import implements

from interfaces import IStatusContainer
from interfaces import IStatusUpdate
from statusupdate import StatusUpdate

logger = logging.getLogger('plonesocial.microblog')


class StatusContainer(Persistent):

    implements(IStatusContainer)
    ANNO_KEY = 'plonesocial.activitystream'

    def __init__(self, context):
        self.context = context
        annotations = IAnnotations(self.context)
        self.__mapping = annotations.get(self.ANNO_KEY, None)
        if self.__mapping is None:
            self.__mapping = OOBTree()
            annotations[self.ANNO_KEY] = self.__mapping

    def _check_value(self, value):
        if not IStatusUpdate.providedBy(value):
            raise ValueError("IStatusUpdate interface not provided.")

    def add(self, text, tags=None):
        value = StatusUpdate(text, tags=tags)
        key = DateTime()
        self.insert(key, value)

    def clear(self):
        return self.__mapping.clear()

    def get(self, key, default=None):
        return self.__mapping.get(key, default=default)

    def insert(self, key, value):
        self._check_value(value)
        result = self.__mapping.insert(key, value)
        event = ObjectAddedEvent(value, newParent=self.context, newName=key)
        notify(event)
        return result

    def items(self, min=None, max=None):
        return self.__mapping.items(min=min, max=max)

    def iteritems(self, min=None, max=None):
        return self.__mapping.iteritems(min=min, max=max)

    def iterkeys(self, min=None, max=None):
        return self.__mapping.iterkeys(min=min, max=max)

    def itervalues(self, min=None, max=None):
        return self.__mapping.itervalues(min=min, max=max)

    def keys(self, min=None, max=None):
        return self.__mapping.keys(min=min, max=max)

    def pop(self, k, d=None):
        _marker = object()
        result = self.__mapping.pop(k, d=_marker)
        if result is _marker:
            return d
        event = ObjectRemovedEvent(result, oldParent=self.context,
                                   oldName=k)
        notify(event)
        return result

    def setdefault(self, k, d):
        return self.__mapping.setdefault(k, d)

    def update(self, collection):
        return self.__mapping.update(collection)

    def values(self, min=None, max=None):
        return self.__mapping.values(min=min, max=max)
