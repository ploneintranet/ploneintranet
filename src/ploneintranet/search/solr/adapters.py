import logging

from scorched import SolrInterface
from zope.component import adapter
from zope.interface import implementer

from .. import base
from ..interfaces import ISearchResponse
from ..interfaces import ISearchResult
from .interfaces import IConnection
from .interfaces import IConnectionConfig
from .interfaces import IQuery
from .interfaces import IResponse
from .search import Search


logger = logging.getLogger(__name__)


@implementer(IConnection)
@adapter(IConnectionConfig)
def connection(config):
    """Adapt Solr configuration to connection/query interface."""
    logger.info('Connecting to Solr on %s', config.url)
    return SolrInterface(config.url)


@implementer(IQuery)
@adapter(IConnection)
def search_query(connection):
    return Search(connection)


@implementer(ISearchResponse)
@adapter(IResponse)
class SearchResponse(base.SearchResponse):
    """A search response object"""

    _spelling_suggestion = None
    _facets = None

    def __iter__(self):
        for doc in self.context:
            yield SearchResult(doc, self)

    def _unpack_facets(self):
        facet_fields = self.context.facet_counts.facet_fields
        named_facets = {}
        for (facet_field, items) in facet_fields.items():
            field_facets = {name for (name, count) in items if count}
            named_facets[facet_field] = field_facets
        return named_facets

    def _unpack_single_suggestion(self):
        spellcheck = self.context.spellcheck
        suggestions = spellcheck.get('suggestions', [])
        if len(suggestions) < 1:
            return None
        query_params = self.context.query_params
        orig_phrase = query_params['phrase']
        collation = spellcheck['collations'][-1]
        suggested = u''.join(x.upper() if y.isupper() else x
                             for (x, y) in zip(collation, orig_phrase))
        return suggested

    @property
    def facets(self):
        if self._facets is None:
            self._facets = self._unpack_facets()
        return self._facets

    @property
    def spell_corrected_search(self):
        if self._spelling_suggestion is None:
            self._spelling_suggestion = self._unpack_single_suggestion()
        return self._spelling_suggestion

    @property
    def total_results(self):
        return self.context.result.numFound


@implementer(ISearchResult)
class SearchResult(base.SearchResult):
    """Build a Search result from a scorched doc (dict)
    and an ISearchResponse
    """

    @property
    def path(self):
        return self.context['path_string']
