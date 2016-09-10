# -*- coding: utf-8 -*-
"""Base module for unittesting."""
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2
import unittest2 as unittest


class PloneintranetCalendarLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        """Set up Zope."""
        # Load ZCML
        import collective.workspace
        self.loadZCML(package=collective.workspace)
        z2.installProduct(app, 'collective.workspace')
        import ploneintranet.network
        self.loadZCML(package=ploneintranet.network)
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
        import ploneintranet.todo
        self.loadZCML(package=ploneintranet.todo)
        import ploneintranet.workspace
        self.loadZCML(package=ploneintranet.workspace)
        import ploneintranet.bookmarks
        self.loadZCML(package=ploneintranet.calendar)

    def setUpPloneSite(self, portal):
        """Set up Plone."""
        # Install into Plone site using portal_setup
        applyProfile(portal, 'ploneintranet.calendar:default')

    def tearDownZope(self, app):
        """Tear down Zope."""
        z2.uninstallProduct(app, 'ploneintranet.calendar')


FIXTURE = PloneintranetCalendarLayer()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,), name="PloneintranetCalendarLayer:Integration")
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,), name="PloneintranetCalendarLayer:Functional")


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = INTEGRATION_TESTING


class FunctionalTestCase(unittest.TestCase):
    """Base class for functional tests."""

    layer = FUNCTIONAL_TESTING
