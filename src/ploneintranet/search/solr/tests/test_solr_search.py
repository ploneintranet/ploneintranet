import unittest

import transaction
from zope.component import getUtility
from zope.interface.verify import verifyObject

from ploneintranet.search.tests import test_base
from ploneintranet.search.interfaces import ISearchResponse
from ploneintranet.search.solr.indexers import (solr_indexing_disable,
                                                solr_indexing_enable)
from ploneintranet.search.solr import testing


class TestConnectionConfig(unittest.TestCase):
    """Unittests for ZCML directive."""

    def _make_utility(self, *args, **kw):
        from ploneintranet.search.solr.solr_search import ConnectionConfig
        return ConnectionConfig(*args, **kw)

    def test_interface_compliance(self):
        from ploneintranet.search.solr.interfaces import IConnectionConfig
        obj = self._make_utility('localhost', '1111', '/solr', 'core1')
        verifyObject(IConnectionConfig, obj)

    def test_url(self):
        obj = self._make_utility('localhost', '1111', '/solr', 'core1')
        self.assertEqual(obj.url, 'http://localhost:1111/solr/core1')


class TestSolrSearch(test_base.SearchTestsBase,
                     testing.FunctionalTestCase):
    """Tests for SiteSearch utility.

    Must be functional because some of the (inherited) tests do commit()

    The actual tests are defined in test_base.
    """

    def _make_utility(self, *args, **kw):
        from ploneintranet.search.solr.solr_search import SiteSearch
        return SiteSearch()

    def _record_debug_info(self, response):
        self._last_response = response.context.original_json

    def setUp(self):
        super(TestSolrSearch, self).setUp()
        from ploneintranet.search.solr.interfaces import IMaintenance
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

    def test_partial_updates(self):
        """Partial updates are not supported."""
        self.doc1.title = u'Star Wars Part 7'
        self.doc1.reindexObject(idxs=['Title'])
        transaction.commit()

        util = self._make_utility()

        response = util.query(u'Wars')
        self.assertEqual(response.total_results, 1)

        # Change a index without changing object.
        self.doc1.reindexObject(idxs=['review_state'])
        transaction.commit()
        response = util.query(u'Wars')
        self.assertEqual(response.total_results, 1)

        self.doc1.description = u'Luke Skywalker'
        self.doc1.reindexObject(idxs=['Description', 'NotASolrIndex'])
        transaction.commit()

        response = util.query(u'Skywalker')
        self.assertEqual(response.total_results, 1)

        self.doc1.title = u'JaJa Binks'
        self.doc1.reindexObject(idxs=['NotASolrIndex'])
        transaction.commit()

        response = util.query(u'JaJa')
        self.assertEqual(response.total_results, 0)


class TestSolrDisableEnable(test_base.ContentSetup,
                            testing.FunctionalTestCase):

    def setUp(self):
        # skip auto-creation of content, do not run ContentSetup.setUp
        testing.FunctionalTestCase.setUp(self)
        self.container = self.layer['portal']
        self.request = self.layer['request']

    def _make_utility(self, *args, **kw):
        from ploneintranet.search.solr.solr_search import SiteSearch
        return SiteSearch()

    def _teardown_content(self):
        from plone import api
        with api.env.adopt_roles(roles=['Manager']):
            for doc in (self.doc1, self.doc2, self.doc3,
                        self.doc4, self.doc5, self.doc6):
                self._delete_content(doc)
            transaction.commit()

    def test_solr_index_disable_enable(self):
        util = self._make_utility()

        # 1st run, indexing disabled
        solr_indexing_disable(self.request)
        self._setup_content(self.container)
        response = self._query(util, 'doc')
        self.assertEqual(response.total_results, 0)

        # teardown and verify
        self._teardown_content()
        response = self._query(util, 'doc')
        self.assertEqual(response.total_results, 0)

        # 2nd run, indexing re-enabled
        solr_indexing_enable(self.request)
        self._setup_content(self.container)
        response = self._query(util, 'doc')
        self.assertEqual(response.total_results, 3)

    def test_solr_index_disable_enable_defaultrequest(self):
        util = self._make_utility()

        # 1st run, indexing disabled
        solr_indexing_disable()
        self._setup_content(self.container)
        response = self._query(util, 'doc')
        self.assertEqual(response.total_results, 0)

        # teardown and verify
        self._teardown_content()
        response = self._query(util, 'doc')
        self.assertEqual(response.total_results, 0)

        # 2nd run, indexing re-enabled
        solr_indexing_enable()
        self._setup_content(self.container)
        response = self._query(util, 'doc')
        self.assertEqual(response.total_results, 3)


class TestSolrPermissions(test_base.PermissionTestsBase,
                          testing.FunctionalTestCase):
    """Integration tests for SiteSearch permissions.

    The actual tests are defined in test_base.
    """

    def _make_utility(self, *args, **kw):
        from ploneintranet.search.solr.solr_search import SiteSearch
        return SiteSearch()

    def _record_debug_info(self, response):
        self._last_response = response.context.original_json
