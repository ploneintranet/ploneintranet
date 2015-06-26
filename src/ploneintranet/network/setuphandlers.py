# -*- coding: utf-8 -*-
import logging
from plone import api
from plone.dexterity.interfaces import IDexterityFTI
from ploneintranet.network.interfaces import INetworkTool
from zope.component.interfaces import ComponentLookupError

log = logging.getLogger(__name__)


def setupVarious(context):
    if context.readDataFile('ploneintranet.network_default.txt') is None:
        return

    log.info('setupVarious')

    # Replace ALL IDublinCore behaviors with our own variant.
    # Doing it like this instead of via profiles/default/types/*.xml
    # - so we don't have to list all types (and will miss some in error)
    # - and we don't have to list all behaviors (and will purge some in error)
    # This can still be overridden per-type in your policy suite types/*xml
    # But there should be no need, this is fully backward compatible
    # and can be cleanly uninstalled
    replace_all_dublincore()


def uninstall(context):
    if context.readDataFile('ploneintranet.network_uninstall.txt') is None:
        return

    log.info('uninstall')
    restore_all_dublincore()

    portal = api.portal.get()
    _remove_persistent_utility(portal)
    # _remove_tool(portal)


def replace_all_dublincore():
    types_tool = api.portal.get_tool('portal_types')
    for fti_id in types_tool.listTypeTitles().keys():
        fti = types_tool.get(fti_id)
        if IDexterityFTI.providedBy(fti):
            replace_dublincore(fti,
                               'plone.app.dexterity',
                               'ploneintranet.network',
                               'replace')


def restore_all_dublincore():
    types_tool = api.portal.get_tool('portal_types')
    for fti_id in types_tool.listTypeTitles().keys():
        fti = types_tool.get(fti_id)
        if IDexterityFTI.providedBy(fti):
            replace_dublincore(fti,
                               'ploneintranet.network',
                               'plone.app.dexterity',
                               'restore')


def replace_dublincore(fti, old, new, msg):
    behaviors = []
    for beh in fti.behaviors:
        # plone.app.dexterity.behaviors.metadata.IDublinCore
        if beh.startswith(old) and beh.endswith('IDublinCore'):
            beh = beh.replace(old, new)
            log.info('%s IDublinCore behavior on %s', msg, fti)
        behaviors.append(beh)
    fti.behaviors = behaviors


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
