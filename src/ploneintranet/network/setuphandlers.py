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
    replace_all_behaviors()


def uninstall(context):
    if context.readDataFile('ploneintranet.network_uninstall.txt') is None:
        return

    log.info('uninstall')
    restore_all_behaviors()

    portal = api.portal.get()
    _remove_persistent_utility(portal)
    # _remove_tool(portal)


REPLACEMENT_BEHAVIORS = [{
    'old': 'plone.app.dexterity.behaviors.metadata.IDublinCore',
    'new': 'ploneintranet.network.behaviors.metadata.IDublinCore',
}, {
    'old': 'plone.app.dexterity.behaviors.metadata.ICategorization',
    'new': 'ploneintranet.network.behaviors.metadata.ICategorization',
}]


def replace_all_behaviors():
    types_tool = api.portal.get_tool('portal_types')
    for fti_id in types_tool.listTypeTitles().keys():
        fti = types_tool.get(fti_id)
        if IDexterityFTI.providedBy(fti):
            for r_beh in REPLACEMENT_BEHAVIORS:
                replace_behavior(fti, r_beh['old'], r_beh['new'], 'replace')


def restore_all_behaviors():
    types_tool = api.portal.get_tool('portal_types')
    for fti_id in types_tool.listTypeTitles().keys():
        fti = types_tool.get(fti_id)
        if IDexterityFTI.providedBy(fti):
            for r_beh in REPLACEMENT_BEHAVIORS:
                replace_behavior(fti, r_beh['new'], r_beh['old'], 'restore')


def replace_behavior(fti, old, new, msg):
    behaviors = []
    for beh in fti.behaviors:
        if beh == old:
            log.info('%s %s behavior on %s', msg, beh, fti)
            beh = new
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
