import unittest2 as unittest

from ploneintranet.pagerank.graph import GRAPH
from ploneintranet.pagerank.testing import\
    PLONEINTRANET_PAGERANK_INTEGRATION

from ploneintranet.pagerank.testing_config import SOCIAL_GRAPH


class TestGraph(unittest.TestCase):

    layer = PLONEINTRANET_PAGERANK_INTEGRATION

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']

    def test_social_following(self):
        """Get the social graph from plonesocial.network
        """
        self.assertEqual(GRAPH.social_following(),
                         SOCIAL_GRAPH)

    def test_content_tree(self):
        """Get the object containment tree
        """
        self.assertEqual(
            GRAPH.content_tree(),
            set([('path:/plone/public', 'path:/plone/public/d1'),
                 ('path:/plone/public/d1', 'path:/plone/public')]))

    def test_content_authors(self):
        """Get the object authorships
        """
        self.assertEqual(
            GRAPH.content_authors(),
            set([('path:/plone/public', 'user:admin'),
                 ('path:/plone/public/d1', 'user:admin'),
                 ('user:admin', 'path:/plone/public'),
                 ('user:admin', 'path:/plone/public/d1')]))

    def test_content_tags(self):
        """Get the object authorships
        """
        self.assertEqual(GRAPH.content_tags(),
                         CONTENT_TAGS)


CONTENT_TAGS = set([('path:/plone/public/d1', 'tag:foo'),
                    ('path:/plone/public/d1', 'tag:nix'),
                    ('tag:nix', 'path:/plone/public/d1'),
                    ('tag:foo', 'path:/plone/public/d1'),
                    ('tag:bar', 'path:/plone/public'),
                    ('tag:foo', 'path:/plone/public'),
                    ('path:/plone/public', 'tag:foo'),
                    ('path:/plone/public', 'tag:bar')])
