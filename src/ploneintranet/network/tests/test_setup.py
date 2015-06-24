# -*- coding: utf-8 -*-
from plone import api
from plone.browserlayer.utils import registered_layers
from ploneintranet.network.testing import IntegrationTestCase

PROJECTNAME = 'ploneintranet.network'


class TestInstall(IntegrationTestCase):

    def setUp(self):
        self.portal = self.layer['portal']

    def test_product_is_installed(self):
        qi = self.portal['portal_quickinstaller']
        self.assertTrue(qi.isProductInstalled(PROJECTNAME))

    def test_addon_layer(self):
        layers = [l.getName() for l in registered_layers()]
        self.assertIn('IPloneIntranetNetworkLayer', layers)


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

    def test_utility_removed(self):
        from zope.component import queryUtility
        from ploneintranet.network.interfaces import INetworkTool
        self.assertIsNone(queryUtility(INetworkTool))

    def test_tool_removed(self):
        self.assertNotIn('ploneintranet_network', self.portal)
