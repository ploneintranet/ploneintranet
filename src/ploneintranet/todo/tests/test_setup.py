# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

from ploneintranet.todo.testing import IntegrationTestCase
from plone import api


class TestInstall(IntegrationTestCase):
    """Test installation of ploneintranet.todo into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if ploneintranet.todo is installed with portal_quickinstaller."""
        self.assertTrue(self.installer.isProductInstalled('ploneintranet.todo'))

    def test_uninstall(self):
        """Test if ploneintranet.todo is cleanly uninstalled."""
        self.installer.uninstallProducts(['ploneintranet.todo'])
        self.assertFalse(self.installer.isProductInstalled('ploneintranet.todo'))

    # browserlayer.xml
    def test_browserlayer(self):
        """Test that IPloneintranetTodoLayer is registered."""
        from ploneintranet.todo.interfaces import IPloneintranetTodoLayer
        from plone.browserlayer import utils
        self.failUnless(IPloneintranetTodoLayer in utils.registered_layers())
