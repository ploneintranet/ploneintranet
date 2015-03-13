# -*- coding: utf-8 -*-
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from zope.configuration import xmlconfig


class PloneIntranetCore(PloneSandboxLayer):

    defaultBases = (
        PLONE_FIXTURE,
    )

    def setUpZope(self, app, configurationContext):
        # Load ZCML for this package
        import ploneintranet.core
        xmlconfig.file(
            'configure.zcml',
            ploneintranet.core,
            context=configurationContext
        )

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ploneintranet.core:minimal')

PLONEINTRANET_CORE_FIXTURE = PloneIntranetCore()
PLONEINTRANET_CORE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONEINTRANET_CORE_FIXTURE, ),
    name='PloneIntranetCore:Integration'
)
