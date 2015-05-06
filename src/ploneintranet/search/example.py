from plone import api
from plone.batching import Batch
from zope.interface import implements

from .interfaces import ISiteSearch
from .results import SearchResponse, SearchResult


class ExampleSiteSearch(object):
    """
    Example implementation of ISiteSearch using the Plone catalog
    """
    implements(ISiteSearch)

    def index(self, obj, attributes=None):
        """
        Plone catalog already indexes the objects
        """
        pass

    def query(self, keywords, facets=None, start=0, step=None):
        """
        Query the catalog using passing facets as kwargs
        and keywords against SearchableText
        :param keywords: The string to pass to SearchableText
        :type keywords: str
        :param facets: The additional fields to filter catalog query by
        :type facets: dict
        :param start: The start offset for results
        :type start: int
        :param step: The maximum number of results to return
        :type step: int
        :return: The results with relevant meta data
        :rtype: `SearchResponse`
        """
        if facets is None:
            facets = {}
        if step is None:
            step = 100
        catalog = api.portal.get_tool('portal_catalog')
        facets.update({
            'SearchableText': keywords
        })
        brains = catalog.searchResults(facets)
        batch = Batch(brains, step, start)
        results = []
        for brain in batch:
            results.append(
                SearchResult(
                    brain['Title'],
                    brain.getPath(),
                    description=brain['Description'],
                    document_type=brain['Type'],
                )
            )
        response_facets = {
            'content_type': {x['Type'] for x in brains},
            'Subject': {y for x in brains for y in x['Subject']},
        }
        response = SearchResponse(
            results,
            total_results=len(results),
            facets=response_facets
        )
        return response
