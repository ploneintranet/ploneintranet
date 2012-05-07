import logging

from AccessControl import getSecurityManager
from BTrees.OOBTree import OOBTree
from DateTime import DateTime
from persistent import Persistent
from persistent.list import PersistentList
from zope.annotation.interfaces import IAnnotations
from zope.app.container.contained import ObjectAddedEvent
from zope.app.container.contained import ObjectRemovedEvent
from zope.event import notify
from zope.interface import Attribute
from zope.interface import Interface
from zope.interface import implements

logger = logging.getLogger('plonesocial.activitystream')


class IActivityContainer(Interface):
    pass


class IActivity(Interface):

    text = Attribute("Text of this activity")
    creator = Attribute("Id of user making this change.")
    date = Attribute("Date (plus time) this activity was made.")
    #attachment = Attribute("File attachment.")
    tags = Attribute("Tags/keywords")


class ActivityContainer(Persistent):

    implements(IActivityContainer)
    ANNO_KEY = 'plonesocial.activitystream'

    def __init__(self, context):
        self.context = context
        annotations = IAnnotations(self.context)
        self.__mapping = annotations.get(self.ANNO_KEY, None)
        if self.__mapping is None:
            self.__mapping = OOBTree()
            annotations[self.ANNO_KEY] = self.__mapping

    def _check_value(self, value):
        if not IActivity.providedBy(value):
            raise ValueError("IActivity interface not provided.")

    def add(self, text, tags=None):
        value = Activity(text, tags=tags)
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


class Activity(Persistent):

    implements(IActivity)

    def __init__(self, text, tags=None):
        logger.info("Initializing activity with text %r and tags %r.",
                    text, tags)
        self.__parent__ = self.__name__ = None
        self.text = text
        sm = getSecurityManager()
        user = sm.getUser()
        self.creator = user.getId() or '(anonymous)'
        self.date = DateTime()
        if tags is None:
            self.tags = PersistentList()
        else:
            self.tags = PersistentList(tags)

    # Act a bit more like a catalog brain:

    def getURL(self):
        return ''

    def getObject(self):
        return self

    def Title(self):
        return self.text
