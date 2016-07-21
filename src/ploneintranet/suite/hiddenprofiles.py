# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import INonInstallable as \
    INonInstallableProfiles
from Products.CMFQuickInstallerTool.interfaces import INonInstallable as \
    INonInstallableProducts
from zope.interface import implementer


@implementer(INonInstallableProducts)
class HiddenProducts(object):

    def getNonInstallableProducts(self):
        """Hide everything but suite:default in quickinstaller"""
        return HIDDEN


@implementer(INonInstallableProfiles)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """Hide some profiles from initial site-creation and quickinstaller"""
        return HIDDEN


HIDDEN = [
    'ploneintranet.activitystream:default',
    'ploneintranet.activitystream:uninstall',
    'ploneintranet.async:default',
    'ploneintranet.async:uninstall',
    'ploneintranet.attachments:default',
    'ploneintranet.attachments:uninstall',
    'ploneintranet.bookmarks:default',
    'ploneintranet.bookmarks:uninstall',
    'ploneintranet.docconv.client:default',
    'ploneintranet.docconv.client:uninstall',
    'ploneintranet.invitations:default',
    'ploneintranet.invitations:uninstall',
    'ploneintranet.layout:default',
    'ploneintranet.layout:uninstall',
    'ploneintranet.library:default',
    'ploneintranet.library:uninstall',
    'ploneintranet.messaging:default',
    'ploneintranet.messaging:uninstall',
    'ploneintranet.microblog:default',
    'ploneintranet.microblog:uninstall',
    'ploneintranet.network:default',
    'ploneintranet.network:uninstall',
    'ploneintranet.notifications:default',
    'ploneintranet.notifications:uninstall',
    'ploneintranet.pagerank:default',
    'ploneintranet.pagerank:uninstall',
    'ploneintranet.search:default',
    'ploneintranet.search:uninstall',
    # 'ploneintranet.suite:default',
    'ploneintranet.suite:uninstall',
    'ploneintranet.theme:default',
    'ploneintranet.theme:uninstall',
    'ploneintranet.themeswitcher:default',
    'ploneintranet.themeswitcher:uninstall',
    'ploneintranet.todo:default',
    'ploneintranet.todo:uninstall',
    'ploneintranet.userprofile:default',
    'ploneintranet.userprofile:uninstall',
    'ploneintranet.workspace:default',
    'ploneintranet.workspace:uninstall',
]
