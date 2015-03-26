# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

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

    def test_uninstall(self):
        """Test if ploneintranet.docconv.client is cleanly uninstalled."""
        self.installer.uninstallProducts(['ploneintranet.docconv.client'])
        self.assertFalse(self.installer.isProductInstalled(
            'ploneintranet.docconv.client'))

    # browserlayer.xml
    def test_browserlayer(self):
        """Test that IPloneintranetDocconv.clientLayer is registered."""
        from ploneintranet.docconv.client.interfaces import (
            IPloneintranetDocconvClientLayer)
        from plone.browserlayer import utils
        self.failUnless(IPloneintranetDocconvClientLayer in
                        utils.registered_layers())
