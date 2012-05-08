import logging
import re

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

    def __init__(self, text):
        self.__parent__ = self.__name__ = None
        self.id = None  # will be set on insertion by IStatusContainer
        self.text = text
        self.date = DateTime()

        self.userid = getSecurityManager().getUser().getId()
        portal_membership = getToolByName(getSite(), 'portal_membership')
        member = portal_membership.getAuthenticatedMember()
        self.creator = member.getUserName()

    @property
    def tags(self):
        return re.findall('#\S*', self.text)

    # Act a bit more like a catalog brain:

    def getURL(self):
        return ''

    def getObject(self):
        return self

    def Title(self):
        return self.text
