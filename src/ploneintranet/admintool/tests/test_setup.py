# -*- coding: utf-8 -*-
'''Setup/installation tests for this package.'''
from plone import api
from plone.browserlayer import utils
from ploneintranet.admintool.browser.interfaces import IPloneintranetAdmintoolLayer  # noqa
from ploneintranet.admintool.testing import IntegrationTestCase


PROJECTNAME = 'ploneintranet.admintool'


class TestInstall(IntegrationTestCase):
    '''Test installation of this  product into Plone.'''

    def setUp(self):
        '''Custom shared utility setup for tests.'''
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        self.assertTrue(self.installer.isProductInstalled(PROJECTNAME))

    def test_browserlayer(self):
        '''Test that IPloneintranetAdmintoolLayer is registered.'''
        self.assertIn(
            IPloneintranetAdmintoolLayer,
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
        '''Test that IPloneintranetAdmintoolLayer is unregistered.'''
        self.assertNotIn(
            IPloneintranetAdmintoolLayer,
            utils.registered_layers()
        )
