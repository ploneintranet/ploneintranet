# -*- coding: utf-8 -*-
"""Base module for unittesting."""

from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.testing import z2

import unittest2 as unittest


class PloneintranetAttachmentsLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        """Set up Zope."""
        # Load ZCML
        import plone.app.discussion
        self.loadZCML(package=plone.app.discussion)
        import five.grok
        self.loadZCML(package=five.grok)
        import plone.dexterity
        self.loadZCML(package=plone.dexterity)
        #TODO: use a content type from ploneintranet instead of the
        # slc.underflow Question and get rid of all these extra packages
        import Products.UserAndGroupSelectionWidget
        self.loadZCML(package=Products.UserAndGroupSelectionWidget)
        import slc.stickystatusmessages
        self.loadZCML(package=slc.stickystatusmessages)
        import slc.mailrouter
        self.loadZCML(package=slc.mailrouter)
        import slc.underflow
        self.loadZCML(package=slc.underflow)

        import ploneintranet.attachments
        self.loadZCML(package=ploneintranet.attachments)
        z2.installProduct(app, 'ploneintranet.attachments')

    def setUpPloneSite(self, portal):
        """Set up Plone."""
        # Install into Plone site using portal_setup
        applyProfile(portal, 'plone.app.discussion:default')
        applyProfile(portal, 'slc.underflow:default')
        applyProfile(portal, 'ploneintranet.attachments:default')

        # Login and create some test content
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)
        portal.invokeFactory('Folder', 'folder')

        # Commit so that the test browser sees these objects
        portal.portal_catalog.clearFindAndRebuild()
        import transaction
        transaction.commit()

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
