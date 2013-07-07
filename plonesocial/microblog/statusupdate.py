import logging
import re
import time

from AccessControl import getSecurityManager
from Products.CMFCore.utils import getToolByName
from DateTime import DateTime
from persistent import Persistent
from zope.interface import implements
from plone.uuid.interfaces import IUUID
from plone.app.uuid.utils import uuidToObject
try:
    from zope.component.hooks import getSite
except ImportError:
    from zope.app.component.hooks import getSite

from interfaces import IStatusUpdate
from utils import get_microblog_context

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
        m_context = get_microblog_context(context)
        if m_context is None:
            self._context_uuid = None
        else:
            self._context_uuid = self._context2uuid(m_context)

    @property
    def context(self):
        if not self._context_uuid:
            return None
        return uuidToObject(self._context_uuid)

    # backward compatibility wrapper
    @property
    def context_uuid(self):
        try:
            return self._context_uuid
        except AttributeError:
            self._context_uuid = None
            return None

    # unittest override point
    def _context2uuid(self, context):
        return IUUID(context)

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
