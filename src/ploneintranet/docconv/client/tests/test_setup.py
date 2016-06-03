# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""
from ploneintranet.docconv.client import handlers
from ploneintranet.docconv.client.decorators import force_synchronous_previews
from ploneintranet.docconv.client.interfaces import (
    IPloneintranetDocconvClientLayer)
from plone.browserlayer.utils import registered_layers
from ploneintranet.docconv.client.testing import IntegrationTestCase
from plone import api


class TestInstall(IntegrationTestCase):
    """Test installation of ploneintranet.docconv.client into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if ploneintranet.docconv.client is installed
        with portal_quickinstaller.
        """
        self.assertTrue(self.installer.isProductInstalled(
            'ploneintranet.docconv.client'))

    def test_catalog(self):
        catalog = api.portal.get_tool('portal_catalog')
        self.assertIn('has_thumbs', catalog.schema())

    def test_uninstall(self):
        """Test if ploneintranet.docconv.client is cleanly uninstalled."""
        self.installer.uninstallProducts(['ploneintranet.docconv.client'])
        self.assertFalse(self.installer.isProductInstalled(
            'ploneintranet.docconv.client'))
        self.assertNotIn(IPloneintranetDocconvClientLayer, registered_layers())
        catalog = api.portal.get_tool('portal_catalog')
        self.assertNotIn('has_thumbs', catalog.schema())
        self.assertNotIn(IPloneintranetDocconvClientLayer, registered_layers())

    def test_browserlayer(self):
        """Test that IPloneintranetDocconv.clientLayer is registered."""
        self.assertIn(IPloneintranetDocconvClientLayer, registered_layers())

    def test_force_synchronous_previews_decorator(self):
        ''' Check that the decorator is correctly:

         - setting ASYNC_ENABLED to False
         - resetting ASYNC_ENABLED to its initial value
        '''
        backup = handlers.ASYNC_ENABLED
        handlers.ASYNC_ENABLED = 'temporary'

        @force_synchronous_previews
        def probe(arg1, arg2, kwarg1=1, kwarg2=2):
            ''' Sample probe returning
            ploneintranet.docconv.client.handlers.ASYNC_ENABLED

            arguments are meaningless
            '''
            return handlers.ASYNC_ENABLED

        self.assertTrue(probe(1, 2) is False)
        self.assertTrue(probe(3, 4, kwarg1=5) != handlers.ASYNC_ENABLED)

        handlers.ASYNC_ENABLED = backup
