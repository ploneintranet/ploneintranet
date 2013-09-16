from zope.interface import implementer
from Products.CMFCore.utils import UniqueObject
from OFS.SimpleItem import SimpleItem

from plonesocial.messaging.interfaces import IMessagingTool
from plonesocial.messaging.messaging import Inboxes


@implementer(IMessagingTool)
class MessagingTool(UniqueObject, SimpleItem, Inboxes):
    """Provide IInboxes as a tool."""

    meta_type = 'plonesocial.messaging tool'
    id = 'plonesocial_messaging'
