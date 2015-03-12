# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from plone import api
from plonesocial.network.interfaces import INetworkTool

import logging

PROJECTNAME = 'plonesocial.network'

logger = logging.getLogger(PROJECTNAME)


def _removeTool(portal):
    portal.manage_delObjects(['plonesocial_network'])


def _removePersistentUtility(portal):
    sm = portal.getSiteManager()
    sm.unregisterUtility(provided=INetworkTool)
    sm.utilities.unsubscribe((), INetworkTool)


def _removeBundleFromRegistry():
    logger.info('Removing bundle reference from registry')

    record = 'plone.bundles/plone-legacy.resources'
    resources = api.portal.get_registry_record(record)
    if u'resource-plonesocial-network-stylesheets' in resources:
        resources.remove(u'resource-plonesocial-network-stylesheets')


def uninstall(portal, reinstall=False):
    if not reinstall:
        profile = 'profile-%s:uninstall' % PROJECTNAME
        setup_tool = getToolByName(portal, 'portal_setup')
        setup_tool.runAllImportStepsFromProfile(profile)
        _removeTool(portal)
        _removePersistentUtility(portal)
        _removeBundleFromRegistry()
        return 'Ran all uninstall steps.'
