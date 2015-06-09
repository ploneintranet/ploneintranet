import unittest

from zope.component import queryUtility
from zope.interface.verify import verifyObject

from .. import testing
from ..interfaces import IConnectionConfig


class TestSolrConfigDirective(unittest.TestCase):

    zcml_template = """\
    <configure xmlns="http://namespaces.zope.org/zope"
               xmlns:five="http://namespaces.zope.org/five"
               xmlns:solr="http://namespaces.ploneintranet.org/search/solr">
        <include package="ploneintranet.search.solr"
                 file="meta.zcml" />
        %s
    </configure>
    """

    layer = testing.INTEGRATION_TESTING

    def test_directive(self):
        util = queryUtility(IConnectionConfig, default=None)
        verifyObject(IConnectionConfig, util)
