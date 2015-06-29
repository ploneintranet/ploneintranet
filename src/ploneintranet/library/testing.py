# -*- coding: utf-8 -*-
import unittest2 as unittest

from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app import testing

from ploneintranet.testing import PLONEINTRANET_FIXTURE


class PloneintranetLibraryLayer(testing.PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,
                    PLONEINTRANET_FIXTURE)

    def setUpZope(self, app, configurationContext):
        import ploneintranet.library
        self.loadZCML(package=ploneintranet.library)

        import ploneintranet.docconv.client
        self.loadZCML(package=ploneintranet.docconv.client)

        import ploneintranet.layout
        self.loadZCML(package=ploneintranet.layout)

    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'ploneintranet.docconv.client:default')
        self.applyProfile(portal, 'ploneintranet.library:default')

    # def tearDownPloneSite(self, portal):
    #     super(PloneintranetLibraryLayer, self).tearDownPloneSite(portal)


FIXTURE = PloneintranetLibraryLayer()
INTEGRATION_TESTING = testing.IntegrationTesting(
    bases=(FIXTURE,), name="PloneintranetLibraryLayer:Integration")
FUNCTIONAL_TESTING = testing.FunctionalTesting(
    bases=(FIXTURE,), name="PloneintranetLibraryLayer:Functional")


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = INTEGRATION_TESTING


class FunctionalTestCase(unittest.TestCase):
    """Base class for functional tests."""

    layer = FUNCTIONAL_TESTING
