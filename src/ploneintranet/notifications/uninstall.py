# -*- coding: utf-8 -*-
from plone import api
from ploneintranet.notifications.interfaces import INotificationsTool
from zope.component.interfaces import ComponentLookupError
import logging

log = logging.getLogger(__name__)


def uninstall(context):
    if context.readDataFile(
            'ploneintranet.notifications_uninstall.txt') is None:
        return
    portal = api.portal.get()
    remove_persistent_utility(portal)


def remove_persistent_utility(portal):
    sm = portal.getSiteManager()
    sm.unregisterUtility(provided=INotificationsTool)
    try:
        util = sm.getUtility(INotificationsTool)
        del util
    except ComponentLookupError:
        pass
    sm.utilities.unsubscribe((), INotificationsTool)
    try:
        del sm.utilities.__dict__['_provided'][INotificationsTool]
        log.info("Removed utility")
    except KeyError:
        pass
