from ploneintranet.pagerank.graph import Graphs


class Compute(object):
    """Compute PageRank per node on the object/user/tag/etc graph."""

    def __init__(self):
        self.graphs = Graphs()
