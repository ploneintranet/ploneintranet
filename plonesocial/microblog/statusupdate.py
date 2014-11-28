import logging
import re
import time

from AccessControl import getSecurityManager
from Products.CMFCore.utils import getToolByName
from DateTime import DateTime
from persistent import Persistent
from zope.interface import implements
from zope.interface import alsoProvides
from plone.uuid.interfaces import IUUID
from plone.app.uuid.utils import uuidToObject
from zope.component.hooks import getSite

from interfaces import IStatusUpdate
from utils import get_microblog_context

from plonesocial.core.integration import PLONESOCIAL
from plonesocial.activitystream.interfaces import IStatusActivityReply

logger = logging.getLogger('plonesocial.microblog')


class StatusUpdate(Persistent):

    implements(IStatusUpdate)

    def __init__(self, text, context=None, thread_id=None):
        self.__parent__ = self.__name__ = None
        self.id = long(time.time() * 1e6)  # modified by IStatusContainer
        self.thread_id = thread_id
        self.text = text
        self.date = DateTime()
        self._init_userid()
        self._init_creator()
        self._init_context(context)

        if thread_id:
            alsoProvides(self, IStatusActivityReply)

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
            # microblog_context UUID
            self._context_uuid = self._context2uuid(m_context)
        if m_context is context:
            self.context_object = None
        else:
            # actual object context
            self.context_object = context

    def replies(self):
        container = PLONESOCIAL.microblog
        for reply in container.thread_values(self.id):
            if IStatusActivityReply.providedBy(reply):
                yield reply

#########################################################################
# FIXME - this now resolves to IMicroblogContext | should resolve object

    @property
    def context(self):
        if not self.context_uuid:
            return None
        return uuidToObject(self._context_uuid)

#########################################################################

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
        try:
            c_obj = self.context_object
        except AttributeError:
            # backward compatibility
            c_obj = self.context_object = None
        return c_obj or self

    def Title(self):
        return self.text

    def getId(self):
        return self.id


try:
    from ploneintranet.attachments.attachments import IAttachmentStoragable
except ImportError:
    IAttachmentStoragable = None


if IAttachmentStoragable is not None:
    from zope import interface
    from zope.annotation.interfaces import IAttributeAnnotatable
    interface.classImplements(StatusUpdate, IAttributeAnnotatable)
    interface.classImplements(StatusUpdate, IAttachmentStoragable)
