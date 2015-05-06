# -*- coding: utf-8 -*-
"""Tests for the search result structures."""

from ..testing import IntegrationTestCase
from ..results import SearchResult
from ..results import SearchResponse


class TestResults(IntegrationTestCase):
    """Test the results structures"""

    def test_search_result_url(self):
        result = SearchResult(
            'item',
            '/plone/path/to/item',
        )
        self.assertEqual(result.url,
                         'http://nohost/plone/path/to/item')

    def test_search_result_preview_image_url(self):
        result = SearchResult(
            'item',
            '/plone/path/to/item',
            preview_path='/plone/path/to/item/preview',
        )
        self.assertEqual(result.preview_image_url,
                         'http://nohost/plone/path/to/item/preview')

    def test_search_response(self):
        res1 = SearchResult(
            'foo',
            '/path/to/foo',
        )
        result_list = [res1]
        response = SearchResponse(result_list)
        self.assertEqual(response.results, result_list)
