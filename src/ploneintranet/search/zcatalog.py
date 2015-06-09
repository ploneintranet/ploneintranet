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

    def _apply_facets(self, query):
        return query

    def _apply_ordering(self, query):
        return query

    def _build_filtered_phrase_query(self, phrase, filters=None):
        query = {'SearchableText': phrase}
        if filters is None:
            filters = {}
        self._validate_query_fields(filters, IQueryFilterFields)
        tags = filters.get('tags')
        if tags is not None:
            query['Subject'] = filters.pop('tags')
        query.update(filters)
        return query

    def _apply_date_range(self, query, start_date=None, end_date=None):
        query = dict(query, created=dict.fromkeys(('query', 'range')))
        created = query['created']
        if all((start_date, end_date)):
            created['query'] = (start_date, end_date)
            created['range'] = 'min:max'
        elif start_date is not None:
            created['query'] = start_date
            created['range'] = 'min'
        else:
            created['query'] = end_date
            created['range'] = 'max'
        return query

    def _paginate(self, query, start, step):
        return dict(query, batch_start=start, batch_step=step)

    def _execute(self, query, debug=False, **kw):
        start = query.pop('batch_start', 0)
        step = query.pop('batch_step', 100)
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog.searchResults(query)
        return Batch(brains, step, start)


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
