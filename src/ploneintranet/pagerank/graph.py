import networkx as nx
from plone import api
from zope.component import queryUtility

from ploneintranet.network.interfaces import INetworkGraph


class Graphs(object):

    def __init__(self):
        self._cache = {}

    def calculate(self):
        """Lazy initialization."""

        # TODO: ensure that this is fully unrestricted / runs as admin

        catalog = api.portal.get_tool('portal_catalog')
        content_tree = []
        content_authors = []
        content_tags = []
        for brain in catalog():
            context = brain.getObject()
            context_path = 'path:%s' % '/'.join(context.getPhysicalPath())

            for child_id in context.objectIds():
                child_path = '%s/%s' % (context_path, child_id)
                # containment is a bidirectional relationship
                content_tree.append((context_path, child_path))
                content_tree.append((child_path, context_path))

            # TODO: add reference links
            # TODO: add text links

            for author in context.creators:
                # authorship is a bidirectional relationship
                content_authors.append((context_path, 'user:%s' % author))
                content_authors.append(('user:%s' % author, context_path))

            # TODO: add sharing

            for tag in context.Subject():
                # tagging is bidirectional between context and tag
                content_tags.append((context_path, 'tag:%s' % tag))
                content_tags.append(('tag:%s' % tag, context_path))

        self._cache['content_tree'] = nx.from_edgelist(
            content_tree,
            create_using=nx.DiGraph())
        self._cache['content_authors'] = nx.from_edgelist(
            content_authors,
            create_using=nx.DiGraph())
        self._cache['content_tags'] = nx.from_edgelist(
            content_tags,
            create_using=nx.DiGraph())

    def social_following(self):
        # FIXME: add proper site context to ploneintranet.network graph
        graph = queryUtility(INetworkGraph)
        result = []
        # FIXME: add proper API accessor to ploneintranet.network graph
        for user in graph._following["user"].keys():
            for following in graph.get_following("user", user):
                result.append((user, following))
        return nx.from_edgelist(result,
                                create_using=nx.DiGraph())

    # TODO: add microblog #tags
    # TODO: add microblog @mentions

    def content_tree(self):
        # lazy init
        if 'content_tree' not in self._cache:
            self.calculate()
        return self._cache['content_tree']

    def content_authors(self):
        # lazy init
        if 'content_authors' not in self._cache:
            self.calculate()
        return self._cache['content_authors']

    def content_tags(self):
        # lazy init
        if 'content_tags' not in self._cache:
            self.calculate()
        return self._cache['content_tags']

    def unify(self, edge_weights={}):
        """Return a unified DiGraph containing all
        subgraphs, with edges weighted differently per subgraph.
        """
        social_following = self.social_following()
        weight = edge_weights.get('social_following', 1)
        for u, v, d in social_following.edges(data=True):
            d['weight'] = weight
        content_tree = self.content_tree()
        weight = edge_weights.get('content_tree', 1)
        for u, v, d in content_tree.edges(data=True):
            d['weight'] = weight
        content_authors = self.content_authors()
        weight = edge_weights.get('content_authors', 1)
        for u, v, d in content_authors.edges(data=True):
            d['weight'] = weight
        content_tags = self.content_tags()
        weight = edge_weights.get('content_tags', 1)
        for u, v, d in content_tags.edges(data=True):
            d['weight'] = weight
        return nx.compose_all([social_following,
                               content_tree,
                               content_authors,
                               content_tags])
