# -*- coding: utf-8 -*-
from plone import api
import logging
from ploneintranet.microblog.interfaces import IMicroblogTool
from zope.component.interfaces import ComponentLookupError

log = logging.getLogger(__name__)


def uninstall(context):
    if context.readDataFile('ploneintranet.microblog_uninstall.txt') is None:
        return
    portal = api.portal.get()
    _removePersistentUtility(portal)


def _removePersistentUtility(portal):
    sm = portal.getSiteManager()
    sm.unregisterUtility(provided=IMicroblogTool)
    try:
        util = sm.getUtility(IMicroblogTool)
        del util
    except ComponentLookupError:
        pass
    sm.utilities.unsubscribe((), IMicroblogTool)
    try:
        del sm.utilities.__dict__['_provided'][IMicroblogTool]
    except KeyError:
        pass
    log.info("Removed IMicroblogTool utility")
