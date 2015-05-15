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
        g.follow('user', 'alex', 'bernard')
        self.assertEqual(['bernard'], list(g.get_following('user', 'alex')))

    def test_user_follow_following(self):
        g = NetworkGraph()
        g.follow('user', 'alex', 'bernard')
        g.follow('user', 'alex', 'caroline')
        g.follow('user', 'alex', 'dick')
        self.assertEqual(['bernard', 'caroline', 'dick'],
                         sorted(list(g.get_following('user', 'alex'))))

    def test_user_follow_unfollow_following(self):
        g = NetworkGraph()
        g.follow('user', 'alex', 'bernard')
        g.follow('user', 'alex', 'caroline')
        g.unfollow('user', 'alex', 'bernard')
        self.assertEqual(['caroline'], list(g.get_following('user', 'alex')))

    def test_user_follow_followers(self):
        g = NetworkGraph()
        g.follow('user', 'alex', 'bernard')
        g.follow('user', 'caroline', 'bernard')
        self.assertEqual(['alex', 'caroline'],
                         sorted(list(g.get_followers('user', 'bernard'))))

    def test_user_follow_unfollow_followers(self):
        g = NetworkGraph()
        g.follow('user', 'alex', 'bernard')
        g.follow('user', 'caroline', 'bernard')
        g.unfollow('user', 'alex', 'bernard')
        self.assertEqual(['caroline'],
                         sorted(list(g.get_followers('user', 'bernard'))))

    def test_string_args(self):
        """BTree keys MUST be of same type. Check that the implementation
        enforces this."""
        g = NetworkGraph()
        self.assertRaises(AssertionError, g.follow, 'user', 1, '2')
        self.assertRaises(AssertionError, g.follow, 'user', '1', 2)
        self.assertRaises(AssertionError, g.unfollow, 'user', 1, '2')
        self.assertRaises(AssertionError, g.unfollow, 'user', '1', 2)
        self.assertRaises(AssertionError, g.get_following, 'user', 2)
        self.assertRaises(AssertionError, g.get_followers, 'user', 2)

    def test_content_follow_unfollow_following(self):
        g = NetworkGraph()
        g.follow('content', 'alex', 'doc1')
        g.follow('content', 'alex', 'doc2')
        g.unfollow('content', 'alex', 'doc1')
        self.assertEqual(['doc2'], list(g.get_following('content', 'alex')))

    def test_tag_follow_unfollow_following(self):
        g = NetworkGraph()
        g.follow('tag', 'alex', 'foo')
        g.follow('tag', 'alex', 'bar')
        g.unfollow('tag', 'alex', 'foo')
        self.assertEqual(['bar'], list(g.get_following('tag', 'alex')))
