# -*- coding: utf-8 -*-
"""Base module for unittesting."""

from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.testing import z2

import unittest2 as unittest


class PloneintranetDocconvClientLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        """Set up Zope."""
        # Load ZCML
        import ploneintranet.attachments
        self.loadZCML(package=ploneintranet.attachments)
        import plone.app.contenttypes
        self.loadZCML(package=plone.app.contenttypes)
        import slc.docconv
        self.loadZCML(package=slc.docconv)
        import collective.documentviewer
        self.loadZCML(package=collective.documentviewer)
        import ploneintranet.attachments
        self.loadZCML(package=ploneintranet.attachments)
        import ploneintranet.docconv.client
        self.loadZCML(package=ploneintranet.docconv.client)
        z2.installProduct(app, 'ploneintranet.docconv.client')

    def setUpPloneSite(self, portal):
        """Set up Plone."""
        # Install into Plone site using portal_setup
        applyProfile(portal, 'plone.app.contenttypes:default')
        applyProfile(portal, 'ploneintranet.docconv.client:default')

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
        z2.uninstallProduct(app, 'ploneintranet.docconv.client')


FIXTURE = PloneintranetDocconvClientLayer()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,), name="PloneintranetDocconvClientLayer:Integration")
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,), name="PloneintranetDocconvClientLayer:Functional")


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = INTEGRATION_TESTING


class FunctionalTestCase(unittest.TestCase):
    """Base class for functional tests."""

    layer = FUNCTIONAL_TESTING
