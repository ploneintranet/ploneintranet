# -*- coding: utf-8 -*-
from ploneintranet.network.graph import NetworkGraph
from ploneintranet.network.interfaces import INetworkGraph
from ploneintranet.network.testing import IntegrationTestCase
from zope.interface.verify import verifyClass


class TestFollowing(IntegrationTestCase):

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

    def test_content_follow_unfollow_following(self):
        g = NetworkGraph()
        g.set_follow('content', 'alex', 'doc1')
        g.set_follow('content', 'alex', 'doc2')
        g.set_unfollow('content', 'alex', 'doc1')
        self.assertEqual(['doc2'], list(g.get_following('content', 'alex')))

    def test_tag_follow_unfollow_following(self):
        g = NetworkGraph()
        g.set_follow('tag', 'alex', 'foo')
        g.set_follow('tag', 'alex', 'bar')
        g.set_unfollow('tag', 'alex', 'foo')
        self.assertEqual(['bar'], list(g.get_following('tag', 'alex')))
