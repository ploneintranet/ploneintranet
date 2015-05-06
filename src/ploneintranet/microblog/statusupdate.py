import logging
from plone import api
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

from ploneintranet.activitystream.interfaces import IStatusActivityReply
from ploneintranet.attachments.attachments import IAttachmentStoragable
from ploneintranet.core.integration import PLONEINTRANET

from zope.annotation.interfaces import IAttributeAnnotatable

logger = logging.getLogger('ploneintranet.microblog')


class StatusUpdate(Persistent):

    implements(
        IAttachmentStoragable,
        IAttributeAnnotatable,
        IStatusUpdate,
    )

    def __init__(self, text, context=None, thread_id=None, mention_ids=None,
                 tags=None):
        self.__parent__ = self.__name__ = None
        self.id = long(time.time() * 1e6)  # modified by IStatusContainer
        self.thread_id = thread_id
        self.text = text
        self.date = DateTime()
        self._init_mentions(mention_ids)
        self._init_userid()
        self._init_creator()
        self._init_context(context)
        self.tags = tags

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

    def _init_mentions(self, mention_ids):
        self.mentions = {}
        if mention_ids is None:
            return
        for userid in mention_ids:
            user = api.user.get(userid)
            if user is not None:
                self.mentions[userid] = user.getProperty('fullname')

    def replies(self):
        container = PLONEINTRANET.microblog
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

    def getCharset(self):
        ''' Return the charset for this file

        BBB: This is a bit weird.
        This method is here because the _prepare_imagedata
        method wants it.

        See https://github.com/ploneintranet/ploneintranet/blob/251c8cf9f1e69c38030b6b6ac2f7c93c86ae1e60/src/ploneintranet/microblog/browser/attachments.py#L45  # noqa
        '''
        return 'utf8'
