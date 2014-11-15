from plone import api
from zope.component import queryUtility

from plonesocial.network.interfaces import INetworkGraph


def get_social_graph():
    # FIXME: add proper site context to plonesocial.network graph
    graph = queryUtility(INetworkGraph)
    result = []
    # FIXME: add proper API accessor to plonesocial.network graph
    for user in graph._following.keys():
        for following in graph.get_following(user):
            result.append((user, following))
    return set(result)


def get_content_graph():
    catalog = api.portal.get_tool('portal_catalog')
    result = []
    for brain in catalog():
        context = brain.getObject()
        source = '/'.join(context.getPhysicalPath())
        for child in context.objectValues():
            target = '/'.join(child.getPhysicalPath())
            result.append((source, target))
            result.append((target, source))
            # TODO: add reference links, text links
            # TODO: add creators, sharing
            # TODO: add tags
    return set(result)
