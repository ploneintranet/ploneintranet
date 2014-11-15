from plone import api
from zope.component import queryUtility

from plonesocial.network.interfaces import INetworkGraph


class Graph(object):

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

            for author in context.Creators():
                # authorship is a bidirectional relationship
                content_authors.append((context_path, 'user:%s' % author))
                content_authors.append(('user:%s' % author, context_path))

            # TODO: add sharing

            for tag in context.Subject():
                # tagging is bidirectional between context and tag
                content_tags.append((context_path, 'tag:%s' % tag))
                content_tags.append(('tag:%s' % tag, context_path))

        self._cache['content_tree'] = set(content_tree)
        self._cache['content_authors'] = set(content_authors)
        self._cache['content_tags'] = set(content_tags)

    def social_following(self):
        # FIXME: add proper site context to plonesocial.network graph
        graph = queryUtility(INetworkGraph)
        result = []
        # FIXME: add proper API accessor to plonesocial.network graph
        for user in graph._following.keys():
            for following in graph.get_following(user):
                result.append((user, following))
        return set(result)

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


GRAPH = Graph()  # costly initialization once
