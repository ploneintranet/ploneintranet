# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

from ploneintranet.readstatus.testing import IntegrationTestCase
from plone import api


class TestInstall(IntegrationTestCase):
    """Test installation of ploneintranet.readstatus into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if ploneintranet.readstatus is installed with portal_quickinstaller."""
        self.assertTrue(self.installer.isProductInstalled('ploneintranet.readstatus'))

    def test_uninstall(self):
        """Test if ploneintranet.readstatus is cleanly uninstalled."""
        self.installer.uninstallProducts(['ploneintranet.readstatus'])
        self.assertFalse(self.installer.isProductInstalled('ploneintranet.readstatus'))

    # browserlayer.xml
    def test_browserlayer(self):
        """Test that IPloneintranetReadstatusLayer is registered."""
        from ploneintranet.readstatus.interfaces import IPloneintranetReadstatusLayer
        from plone.browserlayer import utils
        self.failUnless(IPloneintranetReadstatusLayer in utils.registered_layers())
