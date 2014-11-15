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
        for brain in catalog():
            context = brain.getObject()
            source = '/'.join(context.getPhysicalPath())
            for child in context.objectValues():
                target = '/'.join(child.getPhysicalPath())
                content_tree.append((source, target))
                content_tree.append((target, source))
                # TODO: add reference links, text links
                # TODO: add creators, sharing
                # TODO: add tags
        self._cache['content_tree'] = set(content_tree)

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


GRAPH = Graph()  # costly initialization once
