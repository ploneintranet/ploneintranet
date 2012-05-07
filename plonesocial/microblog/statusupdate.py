import logging

from AccessControl import getSecurityManager
from DateTime import DateTime
from persistent import Persistent
from persistent.list import PersistentList
from zope.interface import implements

from interfaces import IStatusUpdate

logger = logging.getLogger('plonesocial.microblog')


class StatusUpdate(Persistent):

    implements(IStatusUpdate)

    def __init__(self, text, tags=None):
        logger.info("Initializing status update with text %r and tags %r.",
                    text, tags)
        self.__parent__ = self.__name__ = None
        self.text = text
        sm = getSecurityManager()
        user = sm.getUser()
        self.userid = user.getId() or '(anonymous)'
        self.creator = 'todo creator'
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
