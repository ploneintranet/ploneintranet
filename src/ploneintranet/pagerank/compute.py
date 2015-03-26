import logging
import mincemeat
import networkx as nx
from multiprocessing import Process

from ploneintranet.pagerank.graph import Graphs

logging.basicConfig(level=logging.INFO)


class Compute(object):
    """Compute PageRank per node on the object/user/tag/etc graph."""

    def __init__(self):
        self.graphs = Graphs()

    def pagerank(self, edge_weights={}, context=None, context_weight=10):
        G = self.graphs.unify(edge_weights)
        if not context:
            return nx.pagerank(G)
        else:
            weights = {}
            for k in G.nodes():
                weights[k] = 1
            weights[context] = context_weight
            return nx.pagerank(G, personalization=weights)

    def personalized_pageranks(self, edge_weights={}, context_weight=10):
        G = self.graphs.unify(edge_weights)
        result = {}
        for k in G.nodes():
            result[k] = self.pagerank(edge_weights, k, context_weight)
        return result


class ComputeMapReduce(Compute):

    def __init__(self, edge_weights={}, context_weight=10):
        super(ComputeMapReduce, self).__init__()
        self.edge_weights = edge_weights
        self.context_weight = context_weight

    def datasource(self):
        return {key: key for key in self.graphs.unify().nodes()}

    def mapfn(self, k, v):
        yield k, self.pagerank(self.edge_weights, k, self.context_weight)

    def reducefn(self, k, vs):
        return vs

    def mapreduce_pageranks(self, clients=8):
        # Since we are running multiple asyncore-based Clients and a
        # Server in separate threads, we need to specify map={} for the
        # Clients, so they all don't use the (default) global asyncore
        # socket map as the Server...
        logging.info("Starting %d clients...", clients)
        for _ in xrange(clients):
            c = mincemeat.Client()
            c.password = "changeme"
            p = Process(target=c.conn, args=("", mincemeat.DEFAULT_PORT))
            p.start()

        s = mincemeat.Server()
        s.datasource = self.datasource()
        s.mapfn = self.mapfn
        s.reducefn = self.reducefn
        result = s.run_server(password="changeme")
        return result
