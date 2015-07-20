import unittest

from zope.component import getUtility
from zope.interface.verify import verifyObject

from ploneintranet.search.tests import base as base_tests
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


class TestSiteSearchPermssions(IntegrationTestMixin,
                               base_tests.SiteSearchPermissionTestsMixin,
                               testing.IntegrationTestCase):
    """Integration tests for SiteSearch permissions."""
