# -*- coding: utf-8 -*-
from ploneintranet.network.graph import NetworkGraph
from ploneintranet.network.interfaces import INetworkGraph
from ploneintranet.network.testing import IntegrationTestCase
from zope.interface.verify import verifyClass


class TestTags(IntegrationTestCase):

    def test_verify_interface(self):
        self.assertTrue(verifyClass(INetworkGraph, NetworkGraph))

    def test_user_tag(self):
        g = NetworkGraph()
        # alex tags bernard with 'leadership'
        g.tag('user', 'alex', 'bernard', 'leadership')
        self.assertEqual(['leadership'],
                         list(g.get_tags('user', 'bernard', 'alex')))
