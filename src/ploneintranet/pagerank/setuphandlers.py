import transaction
from zope.component import queryUtility

from plonesocial.network.interfaces import INetworkGraph

from ploneintranet.pagerank.testing_config import SOCIAL_GRAPH


def setup_testing(context):

    if context.readDataFile('ploneintranet.pagerank_testing.txt') is None:
        return

    site = context.getSite()

    # replace randomized plonesocial.suite demo network
    # with a deterministic social network
    graph = queryUtility(INetworkGraph)
    graph.clear()
    for (user, follow) in SOCIAL_GRAPH:
        graph.set_follow(user, follow)

    site.public.setSubject(('foo', 'bar'))
    site.public.d1.setSubject(('foo', 'nix'))

    transaction.commit()
