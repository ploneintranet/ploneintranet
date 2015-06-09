import abc
import collections

from plone import api
from zope import globalrequest

from .interfaces import IFacetFields
from .interfaces import IQueryFilterFields
from .interfaces import ISearchResult
from .interfaces import ISearchResponse


def _field_names_from_iface(iface):
    return tuple(dict(iface.namesAndDescriptions(True)))


FEATURE_NOT_IMPLEMENTED = type(
    'FeatureNotImplemented',
    (object,), {
        '__nonzero__': lambda self: False
    }
)()


class NoOpQueryMethod(object):
    """A non-data descriptor that indicates a query feature is not applicable.

    This could either be because a given feature is not supported,
    or that the back-end in use already supports the operation in some
    other way.

    Assigning an instance of this class to a method name which usually
    forms part of an abstract API will result in a `pass through` call.
    """

    def __init__(self, reason='Not supported backend'):
        self._reason = reason

    def __get__(self, obj, type=None):
        reason = self._reason
        if not reason.rstrip().endswith(':'):
            self._reason = reason.format(obj.__module__)
        return self._no_op

    def __repr__(self):
        return '{0.__class__.__name__}(0._reason)'.format(self)

    def __str__(self):
        return self._reason

    def _no_op(self, query, *args, **kw):
        return query


class SearchResult(object):
    """Abstract search result implementation."""

    preview_image_path = None
    highlighted_summary = FEATURE_NOT_IMPLEMENTED

    def __init__(self, context):
        super(SearchResult, self).__init__()
        self.context = context
        self.title = context['Title']
        self.description = context['Description']
        self.friendly_type_name = context['friendly_type_name']
        if context['has_thumbs']:
            self.preview_image_path = '{.path}/docconv_image_thumb.jpg'.format(
                self)
        elif self.friendly_type_name == 'Image':
            self.preview_image_path = '{.path}/@@images/image/preview'.format(
                self)

    def __repr__(self):
        clsnam = type(self).__name__
        state = vars(self)
        attrs = {
            name: state.get(name)
            for name in dict(ISearchResult.namesAndDescriptions())
        }
        format_item = '{name}={value!r}'.format
        attr_state = ', '.join(format_item(name=name, value=value)
                               for (name, value) in attrs.items())
        return '{clsnam}({attrs})'.format(clsnam=clsnam, attrs=attr_state)

    __str__ = __repr__

    def _path_to_url(self, physical_path):
        """
        Generate an absolute url from a physical path
        """
        if physical_path is not None:
            request = globalrequest.getRequest()
            return request.physicalPathToURL(physical_path)
        return None

    @abc.abstractproperty
    def path(self):
        """Return the path URI to the object represented."""

    @property
    def url(self):
        """
        Generate the absolute URL for the indexed document
        :return: The absolute URL to the document in Plone
        :rtype: str
        """
        portal_props = api.portal.get_tool('portal_properties')
        site_props = portal_props.site_properties
        view_types = site_props.getProperty('typesUseViewActionInListings', ())
        url = self._path_to_url(self.path)
        if self.context['portal_type'] in view_types:
            url = '{}/view'.format(url)
        return url

    @property
    def preview_image_url(self):
        """
        Generate the absolute URL for the preview image of the indexed document

        :returns: The absolute URL to the preview image
        :rtype: str
        """
        return self._path_to_url(self.preview_image_path)

    @classmethod
    def from_indexed_result(cls, **kw):
        """Initialize from the keywords of any indexed result.

        :returns: A new search result object.
        :rtype: `SearchResult`
        """
        return cls(kw)


class SearchResponse(collections.Iterable):
    """Base search response object"""

    total_results = FEATURE_NOT_IMPLEMENTED
    spell_corrected_search = FEATURE_NOT_IMPLEMENTED

    def __init__(self, context):
        super(SearchResponse, self).__init__()
        self.context = context

    def __iter__(self):
        for search_result in self.context:
            yield search_result

    @property
    def results(self):
        return self.context


class SiteSearchProtocol:
    """Abstact site search query protocol.

    Implementations of ISiteSearch should register themselves
    with this abc:

        SiteSearchProtocol.register(MySiteSearchImplementation)

    Should an implementation not be able to implement one of the abstract
    methods defined here, it should explicitly declare so.

    Example:

        @implementer(ISiteSearch)
        class MySiteSearch(object):

            _apply_spellchecking = QueryOperationNotApplicable()

    """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def _create_query_object(self, phrase):
        """Return the query object to be executed from the given `phrase`."""

    @abc.abstractmethod
    def _apply_security(self, query):
        """Apply a security filter to the query.

        This should Plone's `allowedRolesAndUsers` index into account.
        Return a copy of the query object with the security filter applied.
        """

    @abc.abstractmethod
    def _apply_filters(self, query, filters=None):
        """Build a filtered phrase query.

        Return a quick object that can be further filtered.
        """

    @abc.abstractmethod
    def _apply_facets(self, query):
        """Apply parameters such that the query response will be faceted.

        Return a copy of the modified `query`.
        """

    @abc.abstractmethod
    def _apply_date_range(self, query, start_date=None, end_date=None):
        """Optionally apply a date range filter to the query.

        `start_date` and `end_date` will never both be `None`.

        Return a copy of the query with date range applied.
        """

    @abc.abstractmethod
    def _paginate(self, query, start, step):
        """Paginate the query object.

        Return a copy of the query object with `start` and `step` pagination
        paramters applied.
        """

    @abc.abstractmethod
    def _apply_ordering(self, query):
        """Return a copy of the query with ordering paramters applied."""

    @abc.abstractmethod
    def _execute(self, query, **kw):
        """Execute the query.

        Return an object that can be adapted to ISearchResponse.
        """

    @abc.abstractmethod
    def _apply_spellchecking(self, query, phrase):
        """Optionally apply paramters such that the query is spellchecked.

        Return a copy of the modified `query`.
        """

    @abc.abstractmethod
    def _apply_debugging(self, phrase, query):
        """Add debugging flags to the query.

        Return a copy of the modified `query`.
        """

    @abc.abstractmethod
    def query(self,
              phrase,
              filters=None,
              start_date=None,
              end_date=None,
              start=0,
              step=None,
              debug=False):
        """Implement a site search query algorithm.

        :seealso: ploneintranet.search.interfaces.ISearchResponse
        :seealso: ploneintranet.search.interfaces.ISiteSearch.query
        """


class SiteSearch(object):
    """Defines the default SiteSearch query implementation.

    Implementors should sub-class this abstract class
    in order to implememnt the default site search algorithm.
    """

    _filter_fields = _field_names_from_iface(IQueryFilterFields)
    _facet_fields = _field_names_from_iface(IFacetFields)

    def _validate_query_fields(self, mapping, iface):
        valid = set(iface)
        requested = set(mapping)
        invalid = requested ^ requested & valid
        if invalid:
            invalid_names = u', '.join(map(repr, invalid))
            msg = u'Invalid {qtype}: {names}'
            qtype = iface.__identifier__.rsplit('.')[-1]
            msg = msg.format(qtype=qtype, names=invalid_names)
            raise LookupError(msg)

    def query(self,
              phrase,
              filters=None,
              start_date=None,
              end_date=None,
              start=0,
              step=None,
              debug=False):
        query = self._create_query_object(phrase)
        if filters is not None:
            query = self._apply_filters(query, filters)
        query = self._apply_facets(query)
        query = self._apply_spellchecking(query, phrase)
        if any((start_date, end_date)):
            query = self._apply_date_range(query, start_date, end_date)
        if step is not None:
            query = self._paginate(query, start, step)
        query = self._apply_ordering(query)
        if debug:
            query = self._add_debuging(query)
        query = self._apply_security(query)
        response = self._execute(query,
                                 phrase=phrase,
                                 start_date=start_date,
                                 end_date=end_date,
                                 start=start,
                                 step=step,
                                 debug=debug)
        return ISearchResponse(response)

SiteSearchProtocol.register(SiteSearch)
