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
        if phrase:
            # Poor man's partial word matching
            phrase = phrase.strip()
            if phrase and not phrase.endswith('*'):
                phrase = phrase + '*'
            return dict(SearchableText=phrase)
        else:
            return {}

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
        query = dict(query, modified=dict.fromkeys(('query', 'range')))
        modified = query['modified']
        if all((start_date, end_date)):
            modified['query'] = (start_date, end_date)
            modified['range'] = 'min:max'
        elif start_date is not None:
            modified['query'] = start_date
            modified['range'] = 'min'
        else:
            modified['query'] = end_date
            modified['range'] = 'max'
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

    facet_fields = base.RegistryProperty('facet_fields')
    facets = {}

    def __init__(self, batched_results):
        all_results = batched_results._sequence
        super(SearchResponse, self).__init__(
            (SearchResult(result, self) for result in batched_results)
        )
        self.total_results = batched_results.sequence_length

        if not self.total_results:
            return

        # Faceting is not supported natively by plone's catalog,
        # so we brute force it here. Recommendation: USE SOLR
        for field in self.facet_fields:
            if field == 'tags':
                catalog_field = 'Subject'
            else:
                catalog_field = field

            if hasattr(all_results[0][catalog_field], '__iter__'):
                # Support keyword-style fields (e.g. tags)
                self.facets[field] = {y for x in all_results
                                      for y in x[catalog_field] if y}
            else:
                self.facets[field] = {x[catalog_field]
                                      for x in all_results if x[catalog_field]}


@implementer(ISearchResult)
class SearchResult(base.SearchResult):
    """Build a Search result from a ZCatalog brain
    and an ISearchResponse
    """

    @property
    def path(self):
        return self.context.getPath()
