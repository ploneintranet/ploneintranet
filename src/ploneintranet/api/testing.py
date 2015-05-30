# -*- coding: utf-8 -*-
"""Base module for unittesting."""
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
import unittest2 as unittest
import ploneintranet.microblog
import ploneintranet.microblog.statuscontainer


class PloneintranetApiLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=ploneintranet.microblog)
        # override sync mode
        ploneintranet.microblog.statuscontainer.MAX_QUEUE_AGE = 0

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ploneintranet.microblog:default')

    def tearDownZope(self, app):
        # reset sync mode
        ploneintranet.microblog.statuscontainer.MAX_QUEUE_AGE = 1000


FIXTURE = PloneintranetApiLayer()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,), name="PloneintranetApiLayer:Integration")
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,), name="PloneintranetApiLayer:Functional")


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = INTEGRATION_TESTING


class FunctionalTestCase(unittest.TestCase):
    """Base class for functional tests."""

    layer = FUNCTIONAL_TESTING
