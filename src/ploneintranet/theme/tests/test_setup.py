# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from plone.browserlayer.utils import registered_layers
from ploneintranet.theme.interfaces import IThemeSpecific
from ploneintranet.theme.testing import PLONEINTRANET_THEME_INTEGRATION_TESTING  # noqa
import unittest2 as unittest


class TestSetup(unittest.TestCase):
    """Test that ploneintranet.theme is properly installed."""

    layer = PLONEINTRANET_THEME_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if ploneintranet.theme is installed."""
        self.assertTrue(
            self.installer.isProductInstalled('ploneintranet.theme'))

    def test_theme_browserlayer(self):
        """Test that IThemeSpecific is registered."""
        self.assertIn(IThemeSpecific, registered_layers())


class TestUninstall(unittest.TestCase):
    """Test that ploneintranet.theme is properly uninstalled."""

    layer = PLONEINTRANET_THEME_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['ploneintranet.theme'])

    def test_uninstall(self):
        """Test if ploneintranet.theme is cleanly uninstalled."""
        self.assertFalse(
            self.installer.isProductInstalled('ploneintranet.theme'))

    def test_theme_browserlayer_removed(self):
        """Test that IThemeSpecific is unregistered."""
        self.assertNotIn(IThemeSpecific, registered_layers())
