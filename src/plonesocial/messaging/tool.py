# -*- coding: utf-8 -*-
from OFS.SimpleItem import SimpleItem
from Products.CMFCore.utils import UniqueObject
from plonesocial.messaging.interfaces import IMessagingTool
from plonesocial.messaging.messaging import Inboxes
from zope.interface import implementer


@implementer(IMessagingTool)
class MessagingTool(UniqueObject, SimpleItem, Inboxes):
    """Provide IInboxes as a tool."""

    meta_type = 'plonesocial.messaging tool'
    id = 'plonesocial_messaging'
