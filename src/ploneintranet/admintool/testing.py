# -*- coding: utf-8 -*-
"""Base module for unittesting."""
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import unittest2 as unittest


class PloneintranetAdmintoolLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        """Set up Zope."""
        import ploneintranet.layout
        self.loadZCML(package=ploneintranet.layout)
        import ploneintranet.docconv.client
        self.loadZCML(package=ploneintranet.docconv.client)
        import ploneintranet.search
        self.loadZCML(package=ploneintranet.search)
        import Products.membrane
        self.loadZCML(package=Products.membrane)
        z2.installProduct(app, 'Products.membrane')
        import ploneintranet.userprofile
        self.loadZCML(package=ploneintranet.userprofile)
        import ploneintranet.admintool
        self.loadZCML(package=ploneintranet.admintool)

    def setUpPloneSite(self, portal):
        """Set up Plone."""
        # Install into Plone site using portal_setup
        applyProfile(portal, 'ploneintranet.admintool:default')

    def tearDownZope(self, app):
        """Tear down Zope."""
        z2.uninstallProduct(app, 'ploneintranet.admintool')


FIXTURE = PloneintranetAdmintoolLayer()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,), name="PloneintranetAdmintoolLayer:Integration")
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,), name="PloneintranetAdmintoolLayer:Functional")


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = INTEGRATION_TESTING


class FunctionalTestCase(unittest.TestCase):
    """Base class for functional tests."""

    layer = FUNCTIONAL_TESTING
