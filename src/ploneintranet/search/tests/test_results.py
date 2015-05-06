# -*- coding: utf-8 -*-
"""Tests for the search result structures."""

from zope.interface.verify import verifyObject
from ploneintranet.search.testing import IntegrationTestCase
from ploneintranet.search.interfaces import ISearchResult
from ploneintranet.search.interfaces import ISearchResponse
from ploneintranet.search.results import SearchResult
from ploneintranet.search.results import SearchResponse


class TestResults(IntegrationTestCase):
    """Test the results structures"""

    def test_search_result(self):
        result = SearchResult()
        self.assertTrue(
            verifyObject(ISearchResult, result)
        )

    def test_search_result_url(self):
        result = SearchResult()
        result.path = '/plone/path/to/item'
        self.assertEqual(result.url,
                         'http://nohost/plone/path/to/item')

    def test_search_result_preview_image_url(self):
        result = SearchResult()
        result.preview_image_path = '/plone/path/to/item/preview'
        self.assertEqual(result.preview_image_url,
                         'http://nohost/plone/path/to/item/preview')

    def test_search_response(self):
        response = SearchResponse()
        self.assertTrue(
            verifyObject(ISearchResponse, response)
        )
