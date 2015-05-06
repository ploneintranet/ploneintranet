"""
Implementations of the ISearchResult and ISearchResponse
"""
from zope.interface import implements

from .interfaces import ISearchResult, ISearchResponse


class SearchResult(object):
    """
    Data structure containing parsed results from search backend
    """
    implements(ISearchResult)

    #: The title of the indexed document (str)
    title = None
    #: The description of the indexed document (str)
    description = None
    #: The relative path to the document in Plone (str)
    path = None
    #: The relative path to the preview image in Plone (str)
    preview_image_path = None
    #: The type of content of the document (str)
    document_type = None
    #: The highlighted summary provided by the backend (str)
    highlighted_summary = None

    @property
    def url(self):
        """
        Generate the absolute URL for the indexed document
        :return: The absolute URL to the document in Plone
        :rtype: str
        """
        return ''

    @property
    def preview_image_url(self):
        """
        Generate the absolute URL for the preview image of the indexed document
        :return: The absolute URL to the preview image
        :rtype: str
        """
        return ''


class SearchResponse(object):
    """
    Data structure containing the parsed response from the search backend
    """
    implements(ISearchResponse)

    #: The list SearchResult objects (list(SearchResult))
    results = None
    #: The collated search query with relevant spell correction (str)
    spell_corrected_search = None
    #: Mapping of faceted field names to available values (dict)
    facets = None
    #: Count of the total results available from the query (int)
    total_results = 0
