from plone import api
from plone.batching import Batch
from zope.component import adapter
from zope.interface import implementer

from . import base
from .interfaces import ISiteSearch
from .interfaces import ISearchResponse
from .interfaces import ISearchResult


@implementer(ISiteSearch)
class SiteSearch(base.SiteSearch):
    """Example implementation of ISiteSearch using the Plone catalog."""

    _apply_facets = base.NoOpQueryMethod()
    _apply_spellchecking = base.NoOpQueryMethod()
    _apply_security = base.NoOpQueryMethod()

    def _create_query_object(self, phrase):
        # Poor man's partial word matching
        phrase = phrase.strip()
        if not phrase.endswith('*'):
            phrase = phrase + '*'
        return dict(SearchableText=phrase)

    def _apply_debug(self, query):
        from pprint import pprint
        pprint(query)
        return query

    def _apply_filters(self, query, filters):
        query = dict(query)
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
            (SearchResult(result, self) for result in batched_results)
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
    """Build a Search result from a ZCatalog brain
    and an ISearchResponse
    """

    @property
    def path(self):
        return self.context.getPath()
