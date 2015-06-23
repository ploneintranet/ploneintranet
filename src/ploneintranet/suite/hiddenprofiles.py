# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import INonInstallable as \
    INonInstallableProfiles
from Products.CMFQuickInstallerTool.interfaces import INonInstallable as \
    INonInstallableProducts
from zope.interface import implementer


@implementer(INonInstallableProducts)
class HiddenProducts(object):

    def getNonInstallableProducts(self):
        """All ploneintranet add-ons are installable"""
        return []


@implementer(INonInstallableProfiles)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """Hide some profiles from initial site-creation and quickinstaller"""
        return [
            'ploneintranet.suite:uninstall',
            'ploneintranet.activitystream:uninstall',
            'ploneintranet.attachments:uninstall',
            'ploneintranet.core:default',
            'ploneintranet.core:uninstall',
            'ploneintranet.docconv.client:uninstall',
            'ploneintranet.invitations:uninstall',
            'ploneintranet.library:uninstall',
            'ploneintranet.messaging:uninstall',
            'ploneintranet.microblog:uninstall',
            'ploneintranet.notifications:uninstall',
            'ploneintranet.network:uninstall',
            'ploneintranet.search:uninstall',
            'ploneintranet.socialsuite:default',
            'ploneintranet.socialsuite:demo',
            'ploneintranet.socialsuite:minimal',
            'ploneintranet.socialsuite:uninstall',
            'ploneintranet.socialtheme:default',
            'ploneintranet.theme:uninstall',
            'ploneintranet.todo:uninstall',
            'ploneintranet.userprofile:uninstall',
            'ploneintranet.workspace:uninstall',
        ]
