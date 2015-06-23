# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from Products.CMFPlone.interfaces import IResourceRegistry
from plone import api
from plone.browserlayer.utils import registered_layers
from plone.registry.interfaces import IRegistry
from ploneintranet.theme.interfaces import IIntranetContentLayer
from ploneintranet.theme.interfaces import IPloneIntranetFormLayer
from ploneintranet.theme.interfaces import IThemeSpecific
from ploneintranet.theme.testing import PLONEINTRANET_THEME_INTEGRATION_TESTING  # noqa
from zope.component import getUtility
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

    def test_content_browserlayer(self):
        """Test that IIntranetContentLayer is registered."""
        self.assertIn(IIntranetContentLayer, registered_layers())

    def test_form_browserlayer(self):
        """Test that IPloneIntranetFormLayer is registered."""
        self.assertIn(IPloneIntranetFormLayer, registered_layers())

    def test_theme_instaled(self):
        from plone.app.theming.utils import getCurrentTheme
        self.assertEqual('ploneintranet.theme', getCurrentTheme())

    def test_resources(self):
        bundles = getUtility(IRegistry).collectionOfInterface(
            IResourceRegistry, prefix="plone.resources")
        self.assertIn('ploneintranet', bundles)

    def test_layout(self):
        self.assertEqual('dashboard.html', self.portal.getLayout())

    def test_actions(self):
        actions = api.portal.get_tool('portal_actions')
        self.assertIn('workspaces', actions.portal_tabs)
        self.assertIn('index_html', actions.portal_tabs)
        self.assertEqual('Dashboard', actions.portal_tabs['index_html'].title)


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

    def test_content_browserlayer_removed(self):
        """Test that IIntranetContentLayer is unregistered."""
        self.assertNotIn(IIntranetContentLayer, registered_layers())

    def test_form_browserlayer_removed(self):
        """Test that IPloneIntranetFormLayer is unregistered."""
        self.assertNotIn(IPloneIntranetFormLayer, registered_layers())

    def test_theme_reset(self):
        from plone.app.theming.utils import getCurrentTheme
        self.assertEqual('barceloneta', getCurrentTheme())

    def test_cssregistry_removed(self):
        bundles = getUtility(IRegistry).collectionOfInterface(
            IResourceRegistry, prefix="plone.resources")
        self.assertNotIn('ploneintranet', bundles)

    def test_layout(self):
        self.assertEqual('listing_view', self.portal.getLayout())
