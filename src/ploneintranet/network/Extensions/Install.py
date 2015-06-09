# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from ploneintranet.network.interfaces import INetworkTool

import logging

PROJECTNAME = 'ploneintranet.network'

logger = logging.getLogger(PROJECTNAME)


def _removeTool(portal):
    portal.manage_delObjects(['ploneintranet_network'])


def _removePersistentUtility(portal):
    sm = portal.getSiteManager()
    sm.unregisterUtility(provided=INetworkTool)
    sm.utilities.unsubscribe((), INetworkTool)


def uninstall(portal, reinstall=False):
    if not reinstall:
        profile = 'profile-%s:uninstall' % PROJECTNAME
        setup_tool = getToolByName(portal, 'portal_setup')
        setup_tool.runAllImportStepsFromProfile(profile)
        _removeTool(portal)
        _removePersistentUtility(portal)
        return 'Ran all uninstall steps.'
