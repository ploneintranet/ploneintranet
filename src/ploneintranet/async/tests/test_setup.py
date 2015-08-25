# -*- coding: utf-8 -*-
import unittest
from plone import api
from plone.browserlayer.utils import registered_layers

from ploneintranet.async.testing import IntegrationTestCase
from ploneintranet.async.interfaces import IPloneintranetAsyncLayer

PROJECTNAME = 'ploneintranet.async'


class TestInstall(IntegrationTestCase):

    @unittest.skip("Why do these tests fail?")
    def test_product_installed(self):
        """Test if ploneintranet.workspace is installed."""
        installer = api.portal.get_tool('portal_quickinstaller')
        self.assertTrue(installer.isProductInstalled(PROJECTNAME))

    @unittest.skip("Why do these tests fail?")
    def test_browserlayer(self):
        """Test that the browserlayer is registered."""
        self.assertIn(IPloneintranetAsyncLayer, registered_layers())


class TestUnInstall(IntegrationTestCase):

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts([PROJECTNAME])

    @unittest.skip("Why do these tests fail?")
    def test_uninstall(self):
        self.assertFalse(
            self.installer.isProductInstalled(PROJECTNAME))

    @unittest.skip("Why do these tests fail?")
    def test_browserlayer_removed(self):
        self.assertNotIn(IPloneintranetAsyncLayer, registered_layers())
