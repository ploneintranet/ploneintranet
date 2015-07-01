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
        g.follow('user', 'bernard', 'alex')  # alex follows bernard
        self.assertEqual(['bernard'], list(g.get_following('user', 'alex')))

    def test_user_follow_utf8(self):
        g = NetworkGraph()
        g.follow('user', 'bernard ☀', 'alex ☃')  # alex follows bernard
        self.assertEqual(
            [u'bernard ☀'], list(g.get_following('user', u'alex ☃')))

    def test_user_follow_following(self):
        g = NetworkGraph()
        g.follow('user', 'bernard', 'alex')
        g.follow('user', 'caroline', 'alex')
        g.follow('user', 'dick', 'alex')
        self.assertEqual(['bernard', 'caroline', 'dick'],
                         sorted(list(g.get_following('user', 'alex'))))

    def test_user_follow_unfollow_following(self):
        g = NetworkGraph()
        g.follow('user', 'bernard', 'alex')
        g.follow('user', 'caroline', 'alex')
        g.unfollow('user', 'bernard', 'alex')
        self.assertEqual(['caroline'], list(g.get_following('user', 'alex')))

    def test_user_follow_followers(self):
        g = NetworkGraph()
        g.follow('user', 'bernard', 'alex')
        g.follow('user', 'bernard', 'caroline')
        self.assertEqual(['alex', 'caroline'],
                         sorted(list(g.get_followers('user', 'bernard'))))

    def test_user_follow_unfollow_followers(self):
        g = NetworkGraph()
        g.follow('user', 'bernard', 'alex')
        g.follow('user', 'bernard', 'caroline')
        g.unfollow('user', 'bernard', 'alex')
        self.assertEqual(['caroline'],
                         sorted(list(g.get_followers('user', 'bernard'))))

    def test_user_is_followed(self):
        g = NetworkGraph()
        g.follow('user', 'bernard', 'alex')
        self.assertTrue(g.is_followed('user', 'bernard', 'alex'))
        self.assertFalse(g.is_followed('user', 'alex', 'bernard'))
        self.assertFalse(g.is_followed('user', 'caroline', 'alex'))
        self.assertFalse(g.is_followed('tag', 'bernard', 'alex'))

    def test_utf8_args(self):
        """BTree keys MUST be of type unicode. Check that the implementation
        enforces this."""
        g = NetworkGraph()
        self.assertRaises(AttributeError, g.follow, 'user', 1, '2')
        self.assertRaises(AttributeError, g.follow, 'user', '1', 2)
        self.assertRaises(AttributeError, g.unfollow, 'user', 1, '2')
        self.assertRaises(AttributeError, g.unfollow, 'user', '1', 2)
        self.assertRaises(AttributeError, g.get_following, 'user', 2)
        self.assertRaises(AttributeError, g.get_followers, 'user', 2)

    def test_content_follow_unfollow_following(self):
        g = NetworkGraph()
        g.follow('content', 'doc1', 'alex')
        g.follow('content', 'doc2', 'alex')
        g.unfollow('content', 'doc1', 'alex')
        self.assertEqual(['doc2'], list(g.get_following('content', 'alex')))

    def test_tag_follow_unfollow_following(self):
        g = NetworkGraph()
        g.follow('tag', 'foo', 'alex')
        g.follow('tag', 'bar', 'alex')
        g.unfollow('tag', 'foo', 'alex')
        self.assertEqual(['bar'], list(g.get_following('tag', 'alex')))
