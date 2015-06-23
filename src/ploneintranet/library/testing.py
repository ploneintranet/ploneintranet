# -*- coding: utf-8 -*-
"""Base module for unittesting ploneintranet.search."""
from contextlib import contextmanager

from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app import testing
from plone import api
import unittest2 as unittest
import ploneintranet.library
import ploneintranet.docconv.client
from ploneintranet.testing import PLONEINTRANET_FIXTURE


TEST_USER_1_NAME = 'icarus'

TEST_USER_1_EMAIL = 'icarus@ploneintranet.org'


@contextmanager
def login_session(username):
    """Temporarily login as another user.

    Re-logging-in the previous user after exiting the context.
    """
    portal = api.portal.get()
    prev_login = None
    try:
        if not api.user.is_anonymous():
            prev_login = api.user.get_current().getUserName()
        testing.logout()
        testing.login(portal, username)
        yield username
    finally:
        testing.logout()
        if prev_login:
            testing.login(portal, prev_login)


class PloneintranetLibraryLayer(testing.PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,
                    PLONEINTRANET_FIXTURE)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=ploneintranet.library)
        self.loadZCML(package=ploneintranet.docconv.client)

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
