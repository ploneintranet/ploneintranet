# -*- coding: utf-8 -*-
from OFS.SimpleItem import SimpleItem
from Products.CMFCore.utils import UniqueObject
from ploneintranet.messaging.interfaces import IMessagingTool
from ploneintranet.messaging.messaging import Inboxes
from zope.interface import implementer


@implementer(IMessagingTool)
class MessagingTool(UniqueObject, SimpleItem, Inboxes):
    """Provide IInboxes as a tool."""

    meta_type = 'ploneintranet.messaging tool'
    id = 'ploneintranet_messaging'
