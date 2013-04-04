import logging
import re
import time

from AccessControl import getSecurityManager
from Products.CMFCore.utils import getToolByName
from DateTime import DateTime
from persistent import Persistent
from zope.interface import implements
from zope.app.component.hooks import getSite

from interfaces import IStatusUpdate

logger = logging.getLogger('plonesocial.microblog')


class StatusUpdate(Persistent):

    implements(IStatusUpdate)

    def __init__(self, text, context=None):
        self.__parent__ = self.__name__ = None
        self.id = long(time.time() * 1e6)  # modified by IStatusContainer
        self.text = text
        self.date = DateTime()
        self._init_userid()
        self._init_creator()
        self._init_context(context)

    # for unittest subclassing
    def _init_userid(self):
        self.userid = getSecurityManager().getUser().getId()

    # for unittest subclassing
    def _init_creator(self):
        portal_membership = getToolByName(getSite(), 'portal_membership')
        member = portal_membership.getAuthenticatedMember()
        self.creator = member.getUserName()

    # for unittest subclassing
    def _init_context(self, context):
        if context is None:
            self._context_UUID = None
        else:
            self._context_UUID = context.UUID

    # backward compatibility wrapper
    @property
    def context_UUID(self):
        try:
            return self._context_UUID
        except AttributeError:
            self._context_UUID = None
            return None

    @property
    def tags(self):
        return [x.strip('#,.;:!$') for x in re.findall('#\S+', self.text)]

    # Act a bit more like a catalog brain:

    def getURL(self):
        return ''

    def getObject(self):
        return self

    def Title(self):
        return self.text
