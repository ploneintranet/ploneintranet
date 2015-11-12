import unittest

from zope.component import getUtility
from zope.interface.verify import verifyObject

from ploneintranet.search.tests import base as base_tests
from ploneintranet.search.interfaces import ISearchResponse
from .. import testing


class TestConnectionConfig(unittest.TestCase):
    """Unittests for ZCML directive."""

    def _make_utility(self, *args, **kw):
        from ..utilities import ConnectionConfig
        return ConnectionConfig(*args, **kw)

    def test_interface_compliance(self):
        from ..interfaces import IConnectionConfig
        obj = self._make_utility('localhost', '1111', '/solr', 'core1')
        verifyObject(IConnectionConfig, obj)

    def test_url(self):
        obj = self._make_utility('localhost', '1111', '/solr', 'core1')
        self.assertEqual(obj.url, 'http://localhost:1111/solr/core1')


class IntegrationTestMixin(object):

    layer = testing.INTEGRATION_TESTING

    def _make_utility(self, *args, **kw):
        from ..utilities import SiteSearch
        return SiteSearch()

    def _record_debug_info(self, response):
        self._last_response = response.context.original_json


class TestSiteSearch(IntegrationTestMixin,
                     base_tests.SiteSearchTestsMixin,
                     testing.IntegrationTestCase):
    """Integration tests for SiteSearch utility.

    The actual tests are in ploneintranet.search.tests.base.
    """

    def setUp(self):
        super(TestSiteSearch, self).setUp()
        from ..interfaces import IMaintenance
        getUtility(IMaintenance).warmup_spellchcker()

    def test_query_with_complex_filters(self):
        util = self._make_utility()
        Q = util.Q
        filters = Q(Title=u'Test Doc 1') | Q(Title=u'Test Doc 2')
        filters &= Q(portal_type='Document')
        response = util.query('Test Doc', filters=filters, debug=True)
        self.assertEqual(response.total_results, 2)

    def test_raw_query_with_complex_filters(self):
        util = self._make_utility()
        query = util.connection.query('Test Doc')
        query = query.filter(query.Q(Title=u'Test Doc 1') |
                             query.Q(Title=u'Test Doc 2') &
                             query.Q(portal_type='Document'))
        response = ISearchResponse(util.execute(query))
        self.assertEqual(response.total_results, 2)


class TestSiteSearchPermssions(IntegrationTestMixin,
                               base_tests.SiteSearchPermissionTestsMixin,
                               testing.IntegrationTestCase):
    """Integration tests for SiteSearch permissions."""
