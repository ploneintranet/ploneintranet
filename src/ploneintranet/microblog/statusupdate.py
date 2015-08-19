# -*- coding=utf-8 -*-
from AccessControl import getSecurityManager
from DateTime import DateTime
from interfaces import IStatusUpdate
from persistent import Persistent
from plone import api
from plone.app.uuid.utils import uuidToObject
from plone.uuid.interfaces import IUUID
from ploneintranet.activitystream.interfaces import IStatusActivityReply
from ploneintranet.attachments.attachments import IAttachmentStoragable
from Products.CMFCore.utils import getToolByName
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.component.hooks import getSite
from zope.interface import alsoProvides
from zope.interface import implements
import logging
import time

logger = logging.getLogger('ploneintranet.microblog')


class StatusUpdate(Persistent):

    implements(
        IAttachmentStoragable,
        IAttributeAnnotatable,
        IStatusUpdate,
    )

    def __init__(
        self,
        text,
        microblog_context=None,
        thread_id=None,
        mention_ids=None,
        tags=None
    ):
        self.__parent__ = self.__name__ = None
        self.id = long(time.time() * 1e6)  # modified by IStatusContainer
        self.thread_id = thread_id
        self.text = text
        self.date = DateTime()
        self._init_mentions(mention_ids)
        self._init_userid()
        self._init_creator()
        self._init_microblog_context(thread_id, microblog_context)
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
    def _init_microblog_context(self, thread_id, context):
        """Set the right security context.
        If thread_id is given, the context of the thread parent is used
        and the given context arg is ignored.

        E.g. a reply globally to a parent post done in a workspace
        takes the security context of the parent post.
        """
        from ploneintranet import api as piapi  # FIXME circular dependency
        if thread_id:
            parent = piapi.microblog.statusupdate.get(thread_id)
            self._microblog_context_uuid = parent._microblog_context_uuid
        # thread_id takes precedence over microblog_context arg!
        else:
            m_context = piapi.microblog.get_microblog_context(context)
            self._microblog_context_uuid = self._context2uuid(m_context)

    def _init_mentions(self, mention_ids):
        self.mentions = {}
        if mention_ids is None:
            return
        for userid in mention_ids:
            user = api.user.get(userid)
            if user is not None:
                self.mentions[userid] = user.getProperty('fullname')

    def replies(self):
        from ploneintranet import api as piapi
        container = piapi.microblog.get_microblog()
        for reply in container.thread_values(self.id):
            if IStatusActivityReply.providedBy(reply):
                yield reply

    @property
    def microblog_context(self):
        uuid = self._microblog_context_uuid
        if not uuid:
            return None
        microblog_context = self._uuid2object(uuid)
        if microblog_context is None:
            raise AttributeError(
                "Microblog context with uuid {0} could not be "
                "retrieved".format(uuid)
            )
        return microblog_context

    # unittest override point
    def _context2uuid(self, context):
        if context is None:
            return None
        return IUUID(context)

    # unittest override point
    def _uuid2object(self, uuid):
        return uuidToObject(uuid)

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

    # BBB this should go after a proper migration has been setup
    @property
    def context(self):
        ''' Be bold about the refactoring in #506!
        '''
        msg = "This is now the microblog_context"
        logger.error(msg)
        raise AttributeError(msg)

    @property
    def context_uuid(self):
        ''' Be bold about the refactoring in #506!
        '''
        msg = "This is now the _microblog_context_uuid"
        logger.error(msg)
        raise AttributeError(msg)
    # /BBB this should go after a proper migration has been setup
