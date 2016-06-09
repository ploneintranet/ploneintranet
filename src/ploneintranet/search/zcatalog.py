# coding=utf-8
from collections import Counter
import Missing
from plone import api
from plone.batching import Batch
from ploneintranet.search import base
from ploneintranet.search.interfaces import ISiteSearch
from ploneintranet.search.interfaces import ISearchResponse
from ploneintranet.search.interfaces import ISearchResult
from zope.component import adapter
from zope.interface import implementer


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
        # Do not apply empty filters to the catalog
        query = {
            key: value
            for key, value in dict(query).iteritems()
            if value or value is False
        }
        filters = {
            key: value
            for key, value in filters.iteritems()
            if value or value is False
        }
        # Rename tags in Subject
        if 'tags' in filters:
            filters['Subject'] = filters.pop('tags')
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

    def execute(self, query, secure=True, **kw):
        ''' The sort parameter
        '''
        start = query.pop('batch_start', 0)
        step = query.pop('batch_step', 100)
        catalog = api.portal.get_tool(name='portal_catalog')
        if secure:
            search = catalog.searchResults
        else:
            search = catalog.unrestrictedSearchResults
        sort = kw.get('sort')
        if sort and isinstance(sort, basestring):
            # valid sort values:
            #  - 'created': sort results ascending by creation date
            #  - '-created': sort results descending by creation date
            #  - 'title': sort results ascending by title
            if sort == 'title':
                sort = 'sortable_title'
            if sort.startswith('-'):
                query['sort_order'] = 'descending'
                query['sort_on'] = sort[1:]
            else:
                query['sort_on'] = sort

        brains = search(query)
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

            values = []
            if hasattr(all_results[0][catalog_field], '__iter__'):
                # Support keyword-style fields (e.g. tags)
                [values.extend(x[catalog_field]) for x in all_results]
            else:
                [values.append(x[catalog_field]) for x in all_results]
            # from ploneintranet.suite.tests import robot_trace; robot_trace()
            if values:
                values = (x for x in values if x != Missing.Value)
                values = [
                    {
                        'name': name,
                        'count': count,
                    }
                    for name, count in Counter(values).iteritems()
                ]
            self.facets[field] = values


@implementer(ISearchResult)
class SearchResult(base.SearchResult):
    """Build a Search result from a ZCatalog brain
    and an ISearchResponse
    """

    def getObject(self):
        return self.context.getObject()

    @property
    def path(self):
        return self.context.getPath()

    @property
    def review_state(self):
        return self.context.review_state
