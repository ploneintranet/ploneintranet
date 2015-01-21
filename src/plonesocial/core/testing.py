# -*- coding: utf-8 -*-
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.tiles.testing import PLONE_APP_TILES_FIXTURE
from zope.configuration import xmlconfig


class PlonesocialCore(PloneSandboxLayer):

    defaultBases = (
        PLONE_APP_TILES_FIXTURE,
    )

    def setUpZope(self, app, configurationContext):
        # Load ZCML for this package
        import plonesocial.core
        xmlconfig.file(
            'configure.zcml',
            plonesocial.core,
            context=configurationContext
        )

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'plonesocial.core:minimal')

PLONESOCIAL_CORE_FIXTURE = PlonesocialCore()
PLONESOCIAL_CORE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONESOCIAL_CORE_FIXTURE, ),
    name='PlonesocialCore:Integration'
)
