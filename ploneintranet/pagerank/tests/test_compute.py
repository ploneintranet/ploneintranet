import networkx as nx
import unittest2 as unittest

from ploneintranet.pagerank.compute import Compute
from ploneintranet.pagerank import testing_config as config
from ploneintranet.pagerank.testing import\
    PLONEINTRANET_PAGERANK_INTEGRATION


class TestCompute(unittest.TestCase):

    layer = PLONEINTRANET_PAGERANK_INTEGRATION

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.compute = Compute()

    def test_init(self):
        self.assertTrue(self.compute.graph is not None)

    def test_pagerank_tags_unweighted(self):
        """A minimal PR test"""
        G = nx.from_edgelist(config.CONTENT_TAGS)
        PR = nx.pagerank(G)
        seq = sorted(PR.items(),
                     key=lambda x: x[1],
                     reverse=True)
        self.assertEqual([(x[0], round(x[1], 2)) for x in seq],
                         [('path:/plone/public', 0.25),
                          ('path:/plone/public/d1', 0.25),
                          ('tag:foo', 0.24),
                          ('tag:bar', 0.13),
                          ('tag:nix', 0.13)])

    def test_pagerank_tags_personalized(self):
        """A minimal personalized PR test
        to demonstrate that taking /plone/public/d1 as personalization context
        increases the pagerank of its tags foo and nix, decreasing tag:bar.
        """
        G = nx.from_edgelist(config.CONTENT_TAGS)
        weights = {}
        for k in G.nodes():
            weights[k] = 1
        weights['path:/plone/public/d1'] = 10
        PR = nx.pagerank(G, personalization=weights)
        seq = sorted(PR.items(),
                     key=lambda x: x[1],
                     reverse=True)
        self.assertEqual([(x[0], round(x[1], 2)) for x in seq],
                         [('path:/plone/public/d1', 0.34),
                          ('tag:foo', 0.23),
                          ('path:/plone/public', 0.19),
                          ('tag:nix', 0.15),
                          ('tag:bar', 0.09)])
