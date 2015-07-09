# -*- coding: utf-8 -*-
from plone import api
from plone.browserlayer.utils import registered_layers
from ploneintranet.library.testing import IntegrationTestCase

from ploneintranet.library.interfaces import IPloneintranetLibraryLayer
from ploneintranet.library.interfaces import ILibraryContentLayer


PROJECTNAME = 'ploneintranet.library'


class TestInstall(IntegrationTestCase):

    def setUp(self):
        super(TestInstall, self).setUp()
        self.portal = self.layer['portal']

    def test_product_is_installed(self):
        qi = self.portal['portal_quickinstaller']
        self.assertTrue(qi.isProductInstalled(PROJECTNAME))

    def test_addon_layer(self):
        self.assertIn(IPloneintranetLibraryLayer, registered_layers())

    def test_app_layer(self):
        self.assertIn(ILibraryContentLayer, registered_layers())


class TestUninstall(IntegrationTestCase):

    def setUp(self):
        super(TestUninstall, self).setUp()
        self.portal = self.layer['portal']
        self.qi = self.portal['portal_quickinstaller']
        with api.env.adopt_roles(['Manager']):
            self.qi.uninstallProducts(products=[PROJECTNAME])

    def test_uninstalled(self):
        self.assertFalse(self.qi.isProductInstalled(PROJECTNAME))

    def test_addon_layer_removed(self):
        self.assertNotIn(IPloneintranetLibraryLayer, registered_layers())

    def test_app_layer_removed(self):
        self.assertNotIn(ILibraryContentLayer, registered_layers())
