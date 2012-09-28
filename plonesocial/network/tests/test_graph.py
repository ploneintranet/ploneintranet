import unittest2 as unittest

from zope.interface.verify import verifyClass

from plonesocial.network.interfaces import INetworkGraph
from plonesocial.network.graph import NetworkGraph


class TestNetworkGraph(unittest.TestCase):

    def test_verify_interface(self):
        self.assertTrue(verifyClass(INetworkGraph, NetworkGraph))

    def test_follow(self):
        g = NetworkGraph()
        g.set_follow('alex', 'bernard')
        self.assertEqual(['bernard'], list(g.get_following('alex')))

    def test_follow_following(self):
        g = NetworkGraph()
        g.set_follow('alex', 'bernard')
        g.set_follow('alex', 'caroline')
        g.set_follow('alex', 'dick')
        self.assertEqual(['bernard', 'caroline', 'dick'],
                         sorted(list(g.get_following('alex'))))

    def test_follow_unfollow_following(self):
        g = NetworkGraph()
        g.set_follow('alex', 'bernard')
        g.set_follow('alex', 'caroline')
        g.set_unfollow('alex', 'bernard')
        self.assertEqual(['caroline'], list(g.get_following('alex')))

    def test_follow_followers(self):
        g = NetworkGraph()
        g.set_follow('alex', 'bernard')
        g.set_follow('caroline', 'bernard')
        self.assertEqual(['alex', 'caroline'],
                         sorted(list(g.get_followers('bernard'))))

    def test_follow_unfollow_followers(self):
        g = NetworkGraph()
        g.set_follow('alex', 'bernard')
        g.set_follow('caroline', 'bernard')
        g.set_unfollow('alex', 'bernard')
        self.assertEqual(['caroline'],
                         sorted(list(g.get_followers('bernard'))))

    def test_string_args(self):
        """BTree keys MUST be of same type. Check that the implementation
        enforces this."""
        g = NetworkGraph()
        self.assertRaises(AssertionError, g.set_follow, 1, '2')
        self.assertRaises(AssertionError, g.set_follow, '1', 2)
        self.assertRaises(AssertionError, g.set_unfollow, 1, '2')
        self.assertRaises(AssertionError, g.set_unfollow, '1', 2)
        self.assertRaises(AssertionError, g.get_following, 2)
        self.assertRaises(AssertionError, g.get_followers, 2)
