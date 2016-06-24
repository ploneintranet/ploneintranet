from zope.component import queryUtility
from zope.interface.verify import verifyObject

from ploneintranet.search.solr import testing
from ploneintranet.search.solr.interfaces import IConnectionConfig


class TestSolrConfigDirective(testing.IntegrationTestCase):

    layer = testing.INTEGRATION_TESTING

    def test_directive(self):
        util = queryUtility(IConnectionConfig, default=None)
        verifyObject(IConnectionConfig, util)
