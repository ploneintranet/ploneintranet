# -*- coding: utf-8 -*-
"""Abstract basis for search implementations."""
import abc
import collections
import logging

from plone import api
from plone.api.validation import at_least_one_of
from ploneintranet import api as pi_api
from scorched.search import LuceneQuery
from zope import globalrequest

from .interfaces import ISearchResult
from .interfaces import ISearchResponse


logger = logging.getLogger(__name__)

# A 'constant' object that evaluates to False
FEATURE_NOT_IMPLEMENTED = type(
    'FeatureNotImplemented',
    (object,), {
        '__nonzero__': lambda self: False
    }
)()


class RegistryProperty(object):
    """A descriptor that gets and sets values from Plone's registry."""

    def __init__(self, field_name, prefix=__package__):
        self._key = '{}.{}'.format(prefix, field_name)

    def __get__(self, obj, type=None):
        return api.portal.get_registry_record(self._key)

    def __set__(self, obj, val):
        api.portal.set_registry_record(self._key, val)


class NoOpQueryMethod(object):
    """A non-data descriptor that indicates a query feature is not applicable.

    This could either be because a given feature is not supported,
    or that the back-end in use already supports the operation in some
    other way.

    Assigning an instance of this class to a method name which usually
    forms part of an abstract API will result in a `pass through` call.
    """

    def __init__(self, reason='Not supported by backend'):
        self._reason = reason

    def __get__(self, obj, obj_type=None):
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
    """Abstract search result implementation.

    Builds a Search result from a generic search result
    and an ISearchResponse.
    This allows result objects to access extra data from
    the ISearchResponse when necessary.
    """

    preview_image_path = None
    highlighted_summary = FEATURE_NOT_IMPLEMENTED

    def __init__(self, context, response):
        super(SearchResult, self).__init__()
        self.context = context
        self.response = response
        self.title = context['Title']
        self.description = context.get('Description')
        self.friendly_type_name = context['friendly_type_name']
        self.portal_type = context['portal_type']
        self.contact_email = context.get('email')
        self.contact_telephone = context.get('telephone')
        self.mimetype = context.get('mimetype', None)
        if context['has_thumbs']:  # indexer in docconv
            # can occur in workspaces AND library
            if self.portal_type in ('Image', 'Document', 'News Item'):
                self.preview_image_path = \
                    '{.path}/@@images/image/preview'.format(self)
            else:
                portal = api.portal.get()
                self.preview_image_path = \
                    pi_api.previews.get_thumbnail_url(
                        portal.restrictedTraverse(self.path.encode('ascii')),
                        relative=True)

        elif self.portal_type == 'Image':
            self.preview_image_path = '{.path}/@@images/image/preview'.format(
                self)
        elif self.portal_type == 'ploneintranet.userprofile.userprofile':
            self.preview_image_path = '{.path}/@@avatar.jpg'.format(self)

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

    @property
    def path(self):
        """Return the path URI to the object represented."""

    def getPath(self):
        return self.path

    def getId(self):
        return self.context['getId']

    @property
    def url(self):
        """Generate the absolute URL for the indexed document.

        :return: The absolute URL to the document in Plone
        :rtype: str
        """
        view_types = api.portal.get_registry_record(
            'plone.types_use_view_action_in_listings')
        url = self._path_to_url(self.path)
        if self.context['portal_type'] in view_types:
            url = '{}/view'.format(url)
        return url

    def getURL(self):
        return self.url

    @property
    def preview_image_url(self):
        """
        Generate the absolute URL for the preview image of the indexed document

        :returns: The absolute URL to the preview image
        :rtype: str
        """
        return self._path_to_url(self.preview_image_path)

    def __getitem__(self, key):
        return self.context[key]

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default


class SearchResponse(collections.Iterable):
    """Base search response object"""

    total_results = FEATURE_NOT_IMPLEMENTED
    spell_corrected_search = FEATURE_NOT_IMPLEMENTED
    facets = FEATURE_NOT_IMPLEMENTED

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
    """Abstract site search query protocol.

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
        """Create a scorched query object for the given ``phrase``.

        Apply any boost paramters based on plone.app.registry entries.

        :return: The query object to be executed from the given ``phrase``.
        """

    @abc.abstractmethod
    def _apply_filters(self, query, filters):
        """Build a filtered phrase query.

        Ensure filters are a subset of those configured via plone.app.registry.

        :return: A query object that can be further filtered.
        """

    @abc.abstractmethod
    def _apply_facets(self, query):
        """Apply parameters such that the query response will be faceted.

        Ensure facets are a subset of those configured via plone.app.registry.

        :return: A copy of the modified `query`.
        """

    @abc.abstractmethod
    def _apply_date_range(self, query, start_date=None, end_date=None):
        """Optionally apply a date range filter to the query.

        `start_date` and `end_date` will never both be `None`.

        :return: A copy of the query with date range applied.
        """

    @abc.abstractmethod
    def _paginate(self, query, start, step):
        """Paginate the query object by ``start`` and ``step``.

        :return: A copy of the query object with `start` and `step` pagination
                 parameters applied.
        """

    @abc.abstractmethod
    def _apply_spellchecking(self, query, phrase):
        """Optionally apply parameters such that the given ``phrase`` is spell-checked.

        Return a copy of the modified `query`.
        """

    @abc.abstractmethod
    def _apply_debug(self, phrase, query):
        """Add any available debugging to the query.

        Return a copy of the modified `query`.
        """

    @abc.abstractmethod
    def query(self,
              phrase=None,
              filters=None,
              start_date=None,
              end_date=None,
              start=0,
              step=None,
              debug=False):
        """Implement a site search query protocol.

        Return an object implementing `ISearchResponse`.

        :seealso: ploneintranet.search.interfaces.ISearchResponse
        :seealso: ploneintranet.search.interfaces.ISiteSearch.query
        """

    @abc.abstractmethod
    def execute(self, query, secure=True, **kw):
        """Execute the query.

        Return an object that can be adapted to ISearchResponse.

        Subclasses should provide the means to filter results based on a
        security context, which should be on by default.

        :param query: The query object.
        :type query: scorched.search.Search
        :param secure: Whether or not to apply security to search results.
        :type secure: bool
        """


class SiteSearch(object):
    """Defines the default SiteSearch query implementation.

    Implementations should sub-class this abstract class
    in order to implement the default site search algorithm.
    """

    facet_fields = RegistryProperty('facet_fields')
    filter_fields = RegistryProperty('filter_fields')
    phrase_fields = RegistryProperty('phrase_fields')

    def __apply_filters(self, query, filters):
        filter_fields = set(self.filter_fields)
        if isinstance(filters, LuceneQuery):
            names = filters.terms.keys()
            for sq in filters.subqueries:
                names.extend(sq.terms.keys())
        else:
            names = filters
        for fname in set(names):
            if fname not in filter_fields:
                msg = 'Invalid facet field {field!r}'.format(field=fname)
                raise LookupError(msg)
        return self._apply_filters(query, filters)

    @at_least_one_of('phrase', 'filters')
    def query(self,
              phrase=None,
              filters=None,
              start_date=None,
              end_date=None,
              start=0,
              step=None,
              debug=False):
        """Return a search response.

        :seealso: ploneintranet.search.interfaces.ISearchResponse
        """
        query = self._create_query_object(phrase)
        if filters is not None:
            query = self.__apply_filters(query, filters)
        query = self._apply_facets(query)
        query = self._apply_spellchecking(query, phrase)
        if any((start_date, end_date)):
            query = self._apply_date_range(query, start_date, end_date)
        if step is not None:
            query = self._paginate(query, start, step)
        if debug:
            query = self._apply_debug(query)
        response = self.execute(query,
                                phrase=phrase,
                                start_date=start_date,
                                end_date=end_date,
                                start=start,
                                step=step,
                                debug=debug)
        return ISearchResponse(response)

SiteSearchProtocol.register(SiteSearch)
