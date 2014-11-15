from plone import api
from zope.component import queryUtility

from plonesocial.network.interfaces import INetworkGraph


class Graph(object):

    def __init__(self):
        self._cache = {}

    def calculate(self):
        """Lazy initialization."""
        catalog = api.portal.get_tool('portal_catalog')
        content_tree = []
        content_authors = []
        for brain in catalog():
            context = brain.getObject()
            context_path = '/'.join(context.getPhysicalPath())
            for child in context.objectValues():
                child_path = '/'.join(child.getPhysicalPath())
                # containment is a bidirectional relationship
                content_tree.append((context_path, child_path))
                content_tree.append((child_path, context_path))
            # TODO: add reference links
            # TODO: add text links
            for author in context.Creators():
                # authorship is a bidirectional relationship
                content_authors.append((context_path, author))
                content_authors.append((author, context_path))
            # TODO: add sharing
            # TODO: add tags
        self._cache['content_tree'] = set(content_tree)
        self._cache['content_authors'] = set(content_authors)

    def social_following(self):
        # FIXME: add proper site context to plonesocial.network graph
        graph = queryUtility(INetworkGraph)
        result = []
        # FIXME: add proper API accessor to plonesocial.network graph
        for user in graph._following.keys():
            for following in graph.get_following(user):
                result.append((user, following))
        return set(result)

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


GRAPH = Graph()  # costly initialization once
