import unittest2 as unittest

from ploneintranet.pagerank.graph import Graph
from ploneintranet.pagerank.testing import\
    PLONEINTRANET_PAGERANK_INTEGRATION

from ploneintranet.pagerank import testing_config as config


class TestGraph(unittest.TestCase):

    layer = PLONEINTRANET_PAGERANK_INTEGRATION

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.graph = Graph()

    def test_social_following(self):
        """Get the social graph from plonesocial.network
        """
        self.assertEqual(self.graph.social_following(),
                         config.SOCIAL_GRAPH)

    def test_content_tree(self):
        """Get the object containment tree
        """
        self.assertEqual(
            self.graph.content_tree(),
            set([('path:/plone/public', 'path:/plone/public/d1'),
                 ('path:/plone/public/d1', 'path:/plone/public')]))

    def test_content_authors(self):
        """Get the object authorships
        """
        self.assertEqual(
            self.graph.content_authors(),
            set([('path:/plone/public', 'user:admin'),
                 ('path:/plone/public/d1', 'user:admin'),
                 ('user:admin', 'path:/plone/public'),
                 ('user:admin', 'path:/plone/public/d1')]))

    def test_content_tags(self):
        """Get the object authorships
        """
        self.assertEqual(self.graph.content_tags(),
                         config.CONTENT_TAGS)
