# -*- coding: utf-8 -*-
"""Base module for unittesting."""
import unittest2 as unittest

from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from zope.configuration import xmlconfig

import plone.app.theming
import ploneintranet.themeswitcher


class PloneintranetThemeswitcherLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=plone.app.theming)
        xmlconfig.file(
            'configure.zcml',
            plone.app.theming,
            context=configurationContext
        )
        self.loadZCML(package=ploneintranet.themeswitcher)
        xmlconfig.file(
            'configure.zcml',
            ploneintranet.themeswitcher,
            context=configurationContext
        )
        # Run the startup hook
        from plone.app.theming.plugins.hooks import onStartup
        onStartup(None)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ploneintranet.themeswitcher:testing')

    def tearDownZope(self, app):
        pass


FIXTURE = PloneintranetThemeswitcherLayer()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,), name="PloneintranetThemeswitcherLayer:Integration")
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,), name="PloneintranetThemeswitcherLayer:Functional")


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = INTEGRATION_TESTING


class FunctionalTestCase(unittest.TestCase):
    """Base class for functional tests."""

    layer = FUNCTIONAL_TESTING
