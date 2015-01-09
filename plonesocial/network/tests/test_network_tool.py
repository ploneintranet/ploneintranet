# -*- coding: utf-8 -*-
from plone import api
from plonesocial.network.interfaces import INetworkGraph
from plonesocial.network.interfaces import INetworkTool
from plonesocial.network.testing import FunctionalTestCase
from plonesocial.network.testing import IntegrationTestCase
from zope.component import queryUtility
import unittest2 as unittest


class TestNetworkTool(IntegrationTestCase):

    def setUp(self):
        self.portal = self.layer['portal']

    def test_network_tool_available(self):
        tool = queryUtility(INetworkTool)
        self.assertTrue(INetworkGraph.providedBy(tool))

    def test_network_tool_uninstalled(self):
        qi = self.portal['portal_quickinstaller']
        with api.env.adopt_roles(['Manager']):
            qi.uninstallProducts(products=['plonesocial.network'])
        self.assertNotIn('plonesocial_network', self.portal)
        tool = queryUtility(INetworkTool, None)
        self.assertIsNone(tool)
