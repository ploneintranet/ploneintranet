# -*- coding: utf-8 -*-
"""Base module for unittesting."""
import base64
import os
import unittest

from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer

from plone.testing import z2

from ploneintranet.testing import PLONEINTRANET_FIXTURE


class PloneintranetAsyncLayer(PloneSandboxLayer):

    defaultBases = (PLONEINTRANET_FIXTURE,)

    def setUp(self):
        """Activate the async stack"""
        self.orig_ASYNC_ENABLED = os.environ.get('ASYNC_ENABLED', 'false')
        self.orig_CELERY_ALWAYS_EAGER = os.environ.get('CELERY_ALWAYS_EAGER',
                                                       'true')
        os.environ['ASYNC_ENABLED'] = 'true'
        os.environ['CELERY_ALWAYS_EAGER'] = 'false'
        super(PloneintranetAsyncLayer, self).setUp()

    def tearDown(self):
        """Restore original environment"""
        super(PloneintranetAsyncLayer, self).tearDown()
        os.environ['ASYNC_ENABLED'] = self.orig_ASYNC_ENABLED
        os.environ['CELERY_ALWAYS_EAGER'] = self.orig_CELERY_ALWAYS_EAGER

    def setUpZope(self, app, configurationContext):
        """Set up Zope."""
        # Load ZCML
        import ploneintranet.async
        self.loadZCML(package=ploneintranet.async)

    def setUpPloneSite(self, portal):
        """Set up Plone."""
        # Install into Plone site using portal_setup
        applyProfile(portal, 'ploneintranet.async:default')

    def tearDownZope(self, app):
        """Tear down Zope."""
        pass


FIXTURE = PloneintranetAsyncLayer()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,), name="PloneintranetAsyncLayer:Integration")
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE, z2.ZSERVER_FIXTURE),  # NB ZServer enabled!
    name="PloneintranetAsyncLayer:Functional")


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = INTEGRATION_TESTING


class FunctionalTestCase(unittest.TestCase):
    """Base class for functional tests."""

    layer = FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.portal.REQUEST
        # fake needed credentials at Post.__init__
        cred = base64.encodestring('admin:secret')
        self.request._auth = 'Basic %s' % cred.strip()
