# -*- coding: utf-8 -*-
from plone import api
import logging
from ploneintranet.network.interfaces import INetworkTool
from zope.component.interfaces import ComponentLookupError

log = logging.getLogger(__name__)


def uninstall(context):
    if context.readDataFile('ploneintranet.network_uninstall.txt') is None:
        return
    portal = api.portal.get()
    _remove_persistent_utility(portal)
    # _remove_tool(portal)


def _remove_persistent_utility(portal):
    sm = portal.getSiteManager()
    sm.unregisterUtility(provided=INetworkTool)
    try:
        util = sm.getUtility(INetworkTool)
        del util
    except ComponentLookupError:
        pass
    sm.utilities.unsubscribe((), INetworkTool)
    try:
        del sm.utilities.__dict__['_provided'][INetworkTool]
    except KeyError:
        pass
    log.info("Removed INetworkTool utility")
