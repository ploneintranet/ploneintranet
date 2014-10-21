# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

from ploneintranet.attachments.testing import IntegrationTestCase
from plone import api


class TestInstall(IntegrationTestCase):
    """Test installation of ploneintranet.attachments into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if ploneintranet.attachments is installed with portal_quickinstaller."""
        self.assertTrue(self.installer.isProductInstalled('ploneintranet.attachments'))

    def test_uninstall(self):
        """Test if ploneintranet.attachments is cleanly uninstalled."""
        self.installer.uninstallProducts(['ploneintranet.attachments'])
        self.assertFalse(self.installer.isProductInstalled('ploneintranet.attachments'))

    # browserlayer.xml
    def test_browserlayer(self):
        """Test that IPloneintranetAttachmentsLayer is registered."""
        from ploneintranet.attachments.interfaces import IPloneintranetAttachmentsLayer
        from plone.browserlayer import utils
        self.failUnless(IPloneintranetAttachmentsLayer in utils.registered_layers())
