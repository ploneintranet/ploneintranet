# -*- coding: utf-8 -*-
"""Base module for unittesting."""

from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import unittest2 as unittest


class PloneintranetAttachmentsLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        """Set up Zope."""
        # Load ZCML
        import plone.app.discussion
        self.loadZCML(package=plone.app.discussion)
        import plone.dexterity
        self.loadZCML(package=plone.dexterity)
        import ploneintranet.microblog
        self.loadZCML(package=ploneintranet.microblog)

        import ploneintranet.attachments
        self.loadZCML(package=ploneintranet.attachments)

        import ploneintranet.docconv.client
        self.loadZCML(package=ploneintranet.docconv.client)
        z2.installProduct(app, 'ploneintranet.attachments')

    def setUpPloneSite(self, portal):
        """Set up Plone."""
        # Install into Plone site using portal_setup
        applyProfile(portal, 'plone.app.discussion:default')
        applyProfile(portal, 'ploneintranet.attachments:default')

    def tearDownZope(self, app):
        """Tear down Zope."""
        z2.uninstallProduct(app, 'ploneintranet.attachments')


FIXTURE = PloneintranetAttachmentsLayer()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,), name="PloneintranetAttachmentsLayer:Integration")
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,), name="PloneintranetAttachmentsLayer:Functional")


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = INTEGRATION_TESTING


class FunctionalTestCase(unittest.TestCase):
    """Base class for functional tests."""

    layer = FUNCTIONAL_TESTING
