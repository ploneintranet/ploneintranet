from zope.component import queryUtility
from zope.interface.verify import verifyObject

from .. import testing
from ..interfaces import IConnectionConfig


class TestSolrConfigDirective(testing.IntegrationTestCase):

    def test_directive(self):
        util = queryUtility(IConnectionConfig, default=None)
        verifyObject(IConnectionConfig, util)
