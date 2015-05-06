"""Tests for the example search API"""
from plone import api

from ..example import ExampleSiteSearch
from ..testing import IntegrationTestCase


class TestExampleSearch(IntegrationTestCase):
    """Test the example search API"""

    def setUp(self):
        self.portal = api.portal.get()
        self.util = ExampleSiteSearch()
        self.doc1 = api.content.create(
            type='Document',
            title='Test Doc',
            description=('This is a test document. '
                         'Hopefully some stuff will be indexed.'),
            container=self.portal,
            subject=('test', 'my-tag',)
        )
        self.doc2 = api.content.create(
            type='Document',
            title='Test Doc 2',
            description=('This is another test document. '
                         'Please let some stuff be indexed.'),
            container=self.portal,
            subject=('test', 'my-other-tag',)
        )

    def test_index(self):
        pass

    def test_query_keywords_only(self):
        response = self.util.query('hopefully')
        self.assertEqual(response.results[0].title, self.doc1.Title())
        self.assertEqual(response.total_results, 1)
        self.assertEqual(response.facets['Type'], {'Page'})
        self.assertEqual(response.facets['Subject'], {'test', 'my-tag'})

    def test_query_facets(self):
        response = self.util.query(
            'stuff',
        )
        self.assertEqual(response.total_results, 2)
        self.assertEqual(response.facets['Subject'],
                         {'test', 'my-tag', 'my-other-tag'})
        # Limit search by a tag from one of the docs
        response = self.util.query(
            'stuff',
            facets={'Subject': ['my-other-tag']}
        )
        self.assertEqual(response.total_results, 1)
        self.assertEqual(response.facets['Subject'],
                         {'test', 'my-other-tag'})
