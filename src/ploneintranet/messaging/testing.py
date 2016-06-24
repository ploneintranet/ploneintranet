# -*- coding: utf-8 -*-
import unittest
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.testing import z2
from zope.configuration import xmlconfig


class PloneIntranetmessagingLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import ploneintranet.messaging
        xmlconfig.file(
            'configure.zcml',
            ploneintranet.messaging,
            context=configurationContext
        )

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ploneintranet.messaging:default')


PLONEINTRANET_MESSAGING_FIXTURE = PloneIntranetmessagingLayer()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONEINTRANET_MESSAGING_FIXTURE,),
    name='PloneIntranetmessagingLayer:Integration'
)
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONEINTRANET_MESSAGING_FIXTURE, z2.ZSERVER_FIXTURE),
    name='PloneIntranetmessagingLayer:Functional'
)


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = INTEGRATION_TESTING


class FunctionalTestCase(unittest.TestCase):
    """Base class for functional tests."""

    layer = FUNCTIONAL_TESTING
