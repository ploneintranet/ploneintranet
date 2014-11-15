import unittest2 as unittest

from ploneintranet.pagerank import graph

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
        self.assertEqual(graph.get_social_graph(),
                         SOCIAL_GRAPH)
