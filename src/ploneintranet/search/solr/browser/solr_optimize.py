from Products.Five.browser import BrowserView
from zope.component import queryUtility
from ploneintranet.search.solr.interfaces import IConnectionConfig, IConnection


class SolrOptimizeView(BrowserView):
    """
    View to start solr optimization.
    """

    def __call__(self):
        self._solr.optimize(waitSearcher=None)

    @property
    def _solr_conf(self):
        return queryUtility(IConnectionConfig)

    @property
    def _solr(self):
        self._connection = IConnection(self._solr_conf)
        return self._connection
