import networkx as nx
import unittest2 as unittest

from ploneintranet.pagerank.compute import Compute, ComputeMapReduce
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
        self.assertTrue(self.compute.graphs is not None)

    def _sorted_pagerank(self, PR):
        seq = sorted(PR.items(),
                     key=lambda x: x[1],
                     reverse=True)
        return [(x[0], round(x[1], 2)) for x in seq]

    def test_pagerank_tags_unweighted(self):
        """A minimal PR test"""
        G = nx.from_edgelist(config.CONTENT_TAGS)
        PR = nx.pagerank(G)
        seq = self._sorted_pagerank(PR)
        self.assertEqual(seq,
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
        seq = self._sorted_pagerank(PR)
        self.assertEqual(seq,
                         [('path:/plone/public/d1', 0.34),
                          ('tag:foo', 0.23),
                          ('path:/plone/public', 0.19),
                          ('tag:nix', 0.15),
                          ('tag:bar', 0.09)])

    def test_pagerank_unweighted_global(self):
        PR = self.compute.pagerank()
        seq = self._sorted_pagerank(PR)
        self.assertEqual(seq[:4],
                         [('path:/plone/public/d1', 0.09),
                          ('path:/plone/public', 0.09),
                          ('lance_stockstill', 0.07),
                          ('pearlie_whitby', 0.06)])

    def test_pagerank_weighted_personalized_tag_nix(self):
        PR = self.compute.pagerank(config.EDGE_WEIGHTS,
                                   context='tag:nix')
        seq = self._sorted_pagerank(PR)
        self.assertEqual(seq[:4],
                         [('path:/plone/public/d1', 0.16),
                          ('path:/plone/public', 0.11),
                          ('tag:nix', 0.1),
                          ('tag:foo', 0.08)])

    def test_pagerank_weighted_personalized_tag_bar(self):
        PR = self.compute.pagerank(config.EDGE_WEIGHTS,
                                   context='tag:bar',
                                   context_weight=100)
        seq = self._sorted_pagerank(PR)
        self.assertEqual(seq[:4],
                         [('path:/plone/public', 0.28),
                          ('tag:bar', 0.21),
                          ('path:/plone/public/d1', 0.15),
                          ('tag:foo', 0.12)])

    def test_personalized_pageranks(self):
        ALL = self.compute.personalized_pageranks(config.EDGE_WEIGHTS)
        seq = self._sorted_pagerank(ALL['tag:nix'])
        self.assertEqual(seq[:4],
                         [('path:/plone/public/d1', 0.16),
                          ('path:/plone/public', 0.11),
                          ('tag:nix', 0.1),
                          ('tag:foo', 0.08)])


class TestComputeMapReduce(unittest.TestCase):

    layer = PLONEINTRANET_PAGERANK_INTEGRATION

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.compute = ComputeMapReduce(config.EDGE_WEIGHTS)

    def BROKEN_test_mapreduce_pageranks(self):
        ALL = self.compute.mapreduce_pageranks()
        seq = self._sorted_pagerank(ALL['tag:nix'])
        self.assertEqual(seq[:4],
                         [('path:/plone/public/d1', 0.16),
                          ('path:/plone/public', 0.11),
                          ('tag:nix', 0.1),
                          ('tag:foo', 0.08)])

#    def test_personalized_pageranks_many(self):
#        for i in xrange(100):
#            self.compute.personalized_pageranks(config.EDGE_WEIGHTS)
