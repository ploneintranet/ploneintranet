# -*- coding: utf-8 -*-
'''Setup/installation tests for this package.'''
from ploneintranet.bookmarks.testing import IntegrationTestCase
from plone import api
from ploneintranet.bookmarks.browser.interfaces import IPloneintranetBookmarksLayer  # noqa
from plone.browserlayer import utils

PROJECTNAME = 'ploneintranet.bookmarks'


class TestInstall(IntegrationTestCase):
    '''Test installation of this  product into Plone.'''

    def setUp(self):
        '''Custom shared utility setup for tests.'''
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        self.assertTrue(self.installer.isProductInstalled(PROJECTNAME))

    def test_browserlayer(self):
        '''Test that IPloneintranetBookmarksLayer is registered.'''
        self.assertIn(
            IPloneintranetBookmarksLayer,
            utils.registered_layers()
        )


class TestUninstall(IntegrationTestCase):
    '''Test this product is properly uninstalled.'''

    def setUp(self):
        '''Custom shared utility setup for tests.'''
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts([PROJECTNAME])

    def test_uninstall(self):
        self.assertFalse(self.installer.isProductInstalled(PROJECTNAME))

    def test_browserlayer(self):
        '''Test that IPloneintranetBookmarksLayer is unregistered.'''
        self.assertNotIn(
            IPloneintranetBookmarksLayer,
            utils.registered_layers()
        )
