# -*- coding: utf-8 -*-
import unittest2 as unittest

from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile

import ploneintranet.layout


class PloneintranetLayoutLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=ploneintranet.layout)
        self.loadZCML(package=ploneintranet.layout.tests)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ploneintranet.layout:default')
        applyProfile(portal, 'ploneintranet.layout.tests:testing')

    def tearDownZope(self, app):
        pass


FIXTURE = PloneintranetLayoutLayer()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,), name="PloneintranetLayoutLayer:Integration")
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,), name="PloneintranetLayoutLayer:Functional")


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = INTEGRATION_TESTING


class FunctionalTestCase(unittest.TestCase):
    """Base class for functional tests."""

    layer = FUNCTIONAL_TESTING
