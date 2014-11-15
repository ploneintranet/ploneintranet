import unittest2 as unittest
from plone import api

from ploneintranet.pagerank.graph import GRAPH
from ploneintranet.pagerank.testing import\
    PLONEINTRANET_PAGERANK_INTEGRATION

from ploneintranet.pagerank.testing_config import SOCIAL_GRAPH


class TestGraph(unittest.TestCase):

    layer = PLONEINTRANET_PAGERANK_INTEGRATION

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']

    def test_get_social_graph(self):
        """Get the social graph from plonesocial.network
        """
        self.assertEqual(GRAPH.social_following(),
                         SOCIAL_GRAPH)

    def test_content_tree(self):
        """Get the object containment tree
        """
        self.assertEqual(GRAPH.content_tree(),
                         set([('/plone/public', '/plone/public/d1'),
                              ('/plone/public/d1', '/plone/public')]))
