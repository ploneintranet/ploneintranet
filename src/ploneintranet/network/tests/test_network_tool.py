# -*- coding: utf-8 -*-
from plone import api
from ploneintranet.network.interfaces import INetworkGraph
from ploneintranet.network.interfaces import INetworkTool
from ploneintranet.network.testing import IntegrationTestCase
from zope.component import queryUtility


class TestNetworkTool(IntegrationTestCase):

    def setUp(self):
        self.portal = self.layer['portal']

    def test_network_tool_available(self):
        tool = queryUtility(INetworkTool)
        self.assertTrue(INetworkGraph.providedBy(tool))

    def test_network_tool_uninstalled(self):
        qi = self.portal['portal_quickinstaller']
        with api.env.adopt_roles(['Manager']):
            qi.uninstallProducts(products=['ploneintranet.network'])
        self.assertNotIn('ploneintranet_network', self.portal)
        tool = queryUtility(INetworkTool, None)
        self.assertIsNone(tool)
