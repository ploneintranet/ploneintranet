# -*- coding: utf-8 -*-
"""Base module for unittesting ploneintranet.search"""
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
import unittest2 as unittest
import ploneintranet.search
import ploneintranet.docconv.client


class PloneintranetSearchLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        """Set up Zope."""
        self.loadZCML(package=ploneintranet.search)
        self.loadZCML(package=ploneintranet.docconv.client)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ploneintranet.docconv.client:default')
        applyProfile(portal, 'ploneintranet.search:default')


FIXTURE = PloneintranetSearchLayer()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,), name="PloneintranetSearchLayer:Integration")
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,), name="PloneintranetSearchLayer:Functional")


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = INTEGRATION_TESTING


class FunctionalTestCase(unittest.TestCase):
    """Base class for functional tests."""

    layer = FUNCTIONAL_TESTING
