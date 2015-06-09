import abc
import collections

from plone import api
from zope import globalrequest

from .interfaces import IFacetFields, IQueryFilterFields, ISearchResult


def _field_names_from_iface(iface):
    return tuple(dict(iface.namesAndDescriptions(True)))


FEATURE_NOT_IMPLEMENTED = type(
    'FeatureNotImplemented',
    (object,), {
        '__nonzero__': lambda self: False
    }
)()


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

    def __repr__(self):
        clsnam = type(self).__name__
        state = vars(self)
        attrs = {
            name: state.get(name)
            for name in set(ISearchResult.namesAndDescriptions())
        }
        attr_state = ', '.join('{name}={value}'.format(name=name, value=value)
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


class SiteSearch(object):
    """Base class for SiteSearch implementations."""

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
