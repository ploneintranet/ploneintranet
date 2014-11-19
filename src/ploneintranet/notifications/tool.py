from zope.interface import implements
from Products.CMFCore.utils import UniqueObject
from OFS.SimpleItem import SimpleItem

from interfaces import INotificationsTool
from queue import Queue


class NotificationsTool(UniqueObject, SimpleItem, Queue):
    """Provide INetworkContainer as a site utility."""

    implements(INotificationsTool)

    meta_type = 'ploneintranet.notifications tool'
    id = 'ploneintranet_notifications'
