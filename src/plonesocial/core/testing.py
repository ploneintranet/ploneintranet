# -*- coding: utf-8 -*-
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from zope.configuration import xmlconfig


class PlonesocialNetwork(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML for this package
        import plonesocial.core
        xmlconfig.file(
            'configure.zcml',
            plonesocial.core,
            context=configurationContext
        )

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'plonesocial.core:default')

PLONESOCIAL_CORE_FIXTURE = PlonesocialNetwork()
PLONESOCIAL_CORE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONESOCIAL_CORE_FIXTURE, ),
    name='PlonesocialNetwork:Integration'
)
