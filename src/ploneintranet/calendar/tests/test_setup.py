# -*- coding: utf-8 -*-
'''Setup/installation tests for this package.'''
from ploneintranet.calendar.testing import IntegrationTestCase
from plone import api
from ploneintranet.calendar.browser.interfaces import IPloneintranetCalendarLayer  # noqa
from plone.browserlayer import utils

PROJECTNAME = 'ploneintranet.calendar'


class TestInstall(IntegrationTestCase):
    '''Test installation of this  product into Plone.'''

    def setUp(self):
        '''Custom shared utility setup for tests.'''
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        self.assertTrue(self.installer.isProductInstalled(PROJECTNAME))

    def test_browserlayer(self):
        '''Test that IPloneintranetCalendarLayer is registered.'''
        self.assertIn(
            IPloneintranetCalendarLayer,
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
        '''Test that IPloneintranetCalendarLayer is unregistered.'''
        self.assertNotIn(
            IPloneintranetCalendarLayer,
            utils.registered_layers()
        )
