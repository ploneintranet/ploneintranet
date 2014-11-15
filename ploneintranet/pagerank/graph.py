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
