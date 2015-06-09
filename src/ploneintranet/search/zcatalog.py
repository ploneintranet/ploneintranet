from datetime import datetime

from plone import api
from plone.batching import Batch
from zope.component import adapter
from zope.interface import implementer

from . import base
from .interfaces import IQueryFilterFields
from .interfaces import ISiteSearch
from .interfaces import ISearchResponse
from .interfaces import ISearchResult


@implementer(ISiteSearch)
class SiteSearch(base.SiteSearch):
    """Example implementation of ISiteSearch using the Plone catalog."""

    def query(self, phrase, filters=None, start_date=datetime.min,
              end_date=datetime.max, start=0, step=None):
        """
        Query the catalog using passing filters as kwargs
        and phrase against SearchableText.

        Also limit the search by the date range given by start_date and
        end_date

        :param phrase: The string to pass to SearchableText
        :type phrase: str
        :param filters: The filters to filter results by
        :type filters: dict
        :param start_date: Earliest created date for results
        :type start_date: datetime.datetime
        :param end_date: Most recent created date for results
        :type end_date: datetime.datetime
        :param start: The offset position in results to start from
        :type start: int
        :param step: The maximum number of results to return
        :type step: int
        :returns: The results as a `SearchResponse` object
        :rtype: `SearchResponse`
        """
        query = {}
        if filters is None:
            filters = {}
        self._validate_query_fields(filters, IQueryFilterFields)
        tags = filters.get('tags')
        if tags is not None:
            query['Subject'] = filters.pop('tags')
        if step is None:
            step = 100
        catalog = api.portal.get_tool('portal_catalog')
        date_range_query = {
            'query': (start_date, end_date),
            'range': 'min:max'
        }
        query.update({
            'SearchableText': phrase,
            'created': date_range_query
        })
        query.update(filters)
        brains = catalog.searchResults(query)
        batch = Batch(brains, step, start)
        return ISearchResponse(batch)


@implementer(ISearchResponse)
@adapter(Batch)
class SearchResponse(base.SearchResponse):
    """Adapter for a ZCatalog search response.

    Implements batching.
    """

    def __init__(self, batched_results):
        all_results = batched_results._sequence
        super(SearchResponse, self).__init__(
            (ISearchResult(result) for result in batched_results)
        )
        self.total_results = batched_results.sequence_length
        self.facets = {
            'friendly_type_name': {
                x['friendly_type_name']
                for x in all_results
                if x['friendly_type_name']
            },
            'tags': {y for x in all_results for y in x['Subject'] if y},
        }


@implementer(ISearchResult)
class SearchResult(base.SearchResult):
    """Adapter for a ZCatalog search result."""

    @property
    def path(self):
        return self.context.getPath()
