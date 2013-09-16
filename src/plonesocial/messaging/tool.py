from zope.interface import implements
from Products.CMFCore.utils import UniqueObject
from OFS.SimpleItem import SimpleItem

from plonesocial.messaging.interfaces import IMessagingTool
from plonesocial.messaging.messaging import Inboxes


class MessagesTool(UniqueObject, SimpleItem, Inboxes):
    """Provide IInboxes as a site utility."""

    implements(IMessagingTool)

    meta_type = 'plonesocial.messaging tool'
    id = 'plonesocial_messaging'
