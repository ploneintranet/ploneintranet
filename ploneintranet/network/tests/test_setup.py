# -*- coding: utf-8 -*-
from plone import api
from plone.browserlayer.utils import registered_layers
from ploneintranet.network.testing import IntegrationTestCase

PROJECTNAME = 'ploneintranet.network'
REGISTRY_ID = 'plone.resources/resource-ploneintranet-network-stylesheets.css'
EXPECTED_CSS = [
    '++resource++ploneintranet.network.stylesheets/ploneintranet_network.css',
]


class TestInstall(IntegrationTestCase):

    def setUp(self):
        self.portal = self.layer['portal']

    def test_product_is_installed(self):
        qi = self.portal['portal_quickinstaller']
        self.assertTrue(qi.isProductInstalled(PROJECTNAME))

    def test_addon_layer(self):
        layers = [l.getName() for l in registered_layers()]
        self.assertIn('IPloneIntranetNetworkLayer', layers)

    def test_cssregistry(self):
        resource_ids = api.portal.get_registry_record(REGISTRY_ID)
        self.assertListEqual(EXPECTED_CSS, resource_ids)


class TestUninstall(IntegrationTestCase):

    def setUp(self):
        self.portal = self.layer['portal']
        self.qi = self.portal['portal_quickinstaller']
        with api.env.adopt_roles(['Manager']):
            self.qi.uninstallProducts(products=[PROJECTNAME])

    def test_uninstalled(self):
        self.assertFalse(self.qi.isProductInstalled(PROJECTNAME))

    def test_addon_layer_removed(self):
        layers = [l.getName() for l in registered_layers()]
        self.assertNotIn('IPloneIntranetNetworkLayer', layers)

    def test_cssregistry_removed(self):
        self.assertRaises(
            api.exc.InvalidParameterError,
            api.portal.get_registry_record,
            [REGISTRY_ID]
        )
