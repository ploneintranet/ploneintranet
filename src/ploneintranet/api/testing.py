# -*- coding: utf-8 -*-
"""Base module for unittesting."""
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing.interfaces import SITE_OWNER_NAME
from plone.app.testing import TEST_USER_ID
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.testing import z2
import unittest2 as unittest

from ploneintranet.testing import PLONEINTRANET_FIXTURE
import ploneintranet.userprofile
import ploneintranet.network
import ploneintranet.microblog
import ploneintranet.microblog.statuscontainer
import ploneintranet.docconv.client
import ploneintranet.theme


class PloneintranetApiLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,
                    PLONEINTRANET_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=ploneintranet.userprofile)
        self.loadZCML(package=ploneintranet.network)
        self.loadZCML(package=ploneintranet.microblog)
        self.loadZCML(package=ploneintranet.docconv.client)
        self.loadZCML(package=ploneintranet.theme)
        z2.installProduct(app, 'Products.membrane')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ploneintranet.userprofile:default')
        applyProfile(portal, 'ploneintranet.network:default')
        applyProfile(portal, 'ploneintranet.microblog:default')
        applyProfile(portal, 'ploneintranet.docconv.client:default')
        applyProfile(portal, 'ploneintranet.theme:default')
        setRoles(portal, TEST_USER_ID, ['Manager'])

    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'Products.membrane')


FIXTURE = PloneintranetApiLayer()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,), name="PloneintranetApiLayer:Integration")
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,), name="PloneintranetApiLayer:Functional")


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.portal.REQUEST

    def login(self, username):
        login(self.portal, username)

    def login_as_portal_owner(self):
        """
        helper method to login as site admin
        """
        z2.login(self.app['acl_users'], SITE_OWNER_NAME)


class FunctionalTestCase(IntegrationTestCase):
    """Base class for functional tests."""

    layer = FUNCTIONAL_TESTING
