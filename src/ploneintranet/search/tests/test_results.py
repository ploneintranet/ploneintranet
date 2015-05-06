# -*- coding: utf-8 -*-
"""Tests for the search result structures."""

from ploneintranet.search.testing import IntegrationTestCase
from ploneintranet.search.results import SearchResult
from plone import api


class TestResults(IntegrationTestCase):
    """Test installation of ploneintranet.todo into Plone."""

    def test_search_result_url(self):
        result = SearchResult()
        portal = api.portal.get()
        test_path = '{.id}/path/to/foo'.format(portal)
        result.path = test_path
        self.assertEqual(result.url,
                         'http://plonesite/path/to/foo')
