# -*- coding: utf-8 -*-

from OFS.SimpleItem import SimpleItem
from Products.CMFCore.utils import UniqueObject
from interfaces import INotificationsTool
from queue import Queues
from zope.interface import implements


class NotificationsTool(UniqueObject, SimpleItem, Queues):
    """Provide INetworkContainer as a site utility."""

    implements(INotificationsTool)

    meta_type = 'ploneintranet.notifications tool'
    id = 'ploneintranet_notifications'
