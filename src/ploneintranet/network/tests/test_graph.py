# -*- coding: utf-8 -*-
from ploneintranet.network.graph import NetworkGraph
from ploneintranet.network.interfaces import INetworkGraph
from ploneintranet.network.testing import IntegrationTestCase
from zope.interface.verify import verifyClass


class TestNetworkGraph(IntegrationTestCase):

    def test_verify_interface(self):
        self.assertTrue(verifyClass(INetworkGraph, NetworkGraph))

    def test_user_follow(self):
        g = NetworkGraph()
        g.set_follow('user', 'alex', 'bernard')
        self.assertEqual(['bernard'], list(g.get_following('user', 'alex')))

    def test_user_follow_following(self):
        g = NetworkGraph()
        g.set_follow('user', 'alex', 'bernard')
        g.set_follow('user', 'alex', 'caroline')
        g.set_follow('user', 'alex', 'dick')
        self.assertEqual(['bernard', 'caroline', 'dick'],
                         sorted(list(g.get_following('user', 'alex'))))

    def test_user_follow_unfollow_following(self):
        g = NetworkGraph()
        g.set_follow('user', 'alex', 'bernard')
        g.set_follow('user', 'alex', 'caroline')
        g.set_unfollow('user', 'alex', 'bernard')
        self.assertEqual(['caroline'], list(g.get_following('user', 'alex')))

    def test_user_follow_followers(self):
        g = NetworkGraph()
        g.set_follow('user', 'alex', 'bernard')
        g.set_follow('user', 'caroline', 'bernard')
        self.assertEqual(['alex', 'caroline'],
                         sorted(list(g.get_followers('user', 'bernard'))))

    def test_user_follow_unfollow_followers(self):
        g = NetworkGraph()
        g.set_follow('user', 'alex', 'bernard')
        g.set_follow('user', 'caroline', 'bernard')
        g.set_unfollow('user', 'alex', 'bernard')
        self.assertEqual(['caroline'],
                         sorted(list(g.get_followers('user', 'bernard'))))

    def test_string_args(self):
        """BTree keys MUST be of same type. Check that the implementation
        enforces this."""
        g = NetworkGraph()
        self.assertRaises(AssertionError, g.set_follow, 'user', 1, '2')
        self.assertRaises(AssertionError, g.set_follow, 'user', '1', 2)
        self.assertRaises(AssertionError, g.set_unfollow, 'user', 1, '2')
        self.assertRaises(AssertionError, g.set_unfollow, 'user', '1', 2)
        self.assertRaises(AssertionError, g.get_following, 'user', 2)
        self.assertRaises(AssertionError, g.get_followers, 'user', 2)
