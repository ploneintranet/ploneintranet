import collections
import logging

from scorched import SolrInterface
from scorched import search
from zope.component import adapter
from zope.interface import implementer

from . import base
from .interfaces import ISearchResponse
from .interfaces import ISearchResult
from .interfaces import IConnection
from .interfaces import IConnectionConfig
from .interfaces import IQuery
from .interfaces import IResponse


logger = logging.getLogger(__name__)


@implementer(IConnection)
@adapter(IConnectionConfig)
def connection(config):
    """Adapt Solr configuration to connection/query interface."""
    logger.info('Connecting to Solr on %s', config.url)
    return SolrInterface(config.url)


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
        collated = spellcheck['collations'][-1]
        return collated

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


class SpellcheckOptions(search.Options):
    """Alternate SpellcheckOptions implementation.

    This implements sub-options for the Solr spellchecker.
    The scorched implementation just allows turning it on.

    This may be pushed back upstream if deemed successfull.
    """
    option_name = 'spellcheck'
    opts = {
        'accuracy': float,
        'collate': bool,
        'maxCollations': int,
        'onlyMorePopular': bool,
        'extendedResults': bool,
        'q': str,
        'reload': bool,
        'build': bool,
    }

    def __init__(self, original=None):
        super(SpellcheckOptions, self).__init__()
        fields = collections.defaultdict(dict)
        self.fields = getattr(original, 'fields', fields)

    def field_names_in_opts(self, opts, fields):
        if fields:
            opts[self.option_name] = True


class Search(search.SolrSearch):

    def _init_common_modules(self):
        super(Search, self)._init_common_modules()
        self.spellchecker = SpellcheckOptions()

    def spellcheck(self, **kw):
        newself = self.clone()
        spellchecker = newself.spellchecker
        query = kw.get('q', u'')
        # XXX: unicode?
        if isinstance(query, unicode):
            kw['q'] = query.encode('utf-8')
        spellchecker.update(**kw)
        return newself


@implementer(IQuery)
@adapter(IConnection)
def search_query(connection):
    return Search(connection)
