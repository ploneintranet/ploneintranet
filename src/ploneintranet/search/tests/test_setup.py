# -*- coding: utf-8 -*-
from plone import api
from plone.browserlayer.utils import registered_layers
from ploneintranet.search.testing import IntegrationTestCase

PROJECTNAME = 'ploneintranet.search'


class TestInstall(IntegrationTestCase):

    def setUp(self):
        super(TestInstall, self).setUp()
        self.portal = self.layer['portal']

    def test_product_is_installed(self):
        qi = self.portal['portal_quickinstaller']
        self.assertTrue(qi.isProductInstalled(PROJECTNAME))

    def test_addon_layer(self):
        layers = [l.getName() for l in registered_layers()]
        self.assertIn('IPloneintranetSearchLayer', layers)

    def test_index_installed(self):
        catalog = api.portal.get_tool('portal_catalog')
        self.assertIn('friendly_type_name', catalog.indexes())
        self.assertIn('friendly_type_name', catalog.schema())


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
        layers = [l.getName() for l in registered_layers()]
        self.assertNotIn('IPloneintranetSearchLayer', layers)

    def test_index_removed(self):
        catalog = api.portal.get_tool('portal_catalog')
        self.assertNotIn('friendly_type_name', catalog.indexes())
        self.assertNotIn('friendly_type_name', catalog.schema())
