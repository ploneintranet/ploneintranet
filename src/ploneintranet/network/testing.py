# -*- coding: utf-8 -*-
"""Base module for unittesting."""

from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import login
from plone.testing import z2


import unittest2 as unittest


class PloneintranetNetworkLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        """Set up Zope."""
        # Load ZCML
        import ploneintranet.network
        self.loadZCML(package=ploneintranet.network)
        # like statusupdates
        import ploneintranet.microblog
        self.loadZCML(package=ploneintranet.microblog)
        # follow users
        import ploneintranet.userprofile
        self.loadZCML(package=ploneintranet.userprofile)
        # needed for follow users
        z2.installProduct(app, 'Products.membrane')
        z2.installProduct(app, 'collective.indexing')

    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'Products.membrane')
        z2.uninstallProduct(app, 'collective.indexing')

    def setUpPloneSite(self, portal):
        """Set up Plone."""
        # Install into Plone site using portal_setup
        applyProfile(portal, 'ploneintranet.network:default')
        applyProfile(portal, 'ploneintranet.microblog:default')
        applyProfile(portal, 'ploneintranet.userprofile:default')


FIXTURE = PloneintranetNetworkLayer()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,), name='PloneintranetNetworkLayer:Integration')
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,), name='PloneintranetNetworkLayer:Functional')


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = INTEGRATION_TESTING

    def login(self, username):
        login(self.portal, username)


class FunctionalTestCase(unittest.TestCase):
    """Base class for functional tests."""

    layer = FUNCTIONAL_TESTING
