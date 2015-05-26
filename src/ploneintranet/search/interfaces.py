""" Interfaces for search API
"""
from zope.interface import Interface
from zope.interface import Attribute
from . import _


class ISiteSearch(Interface):
    """
    Interface defining a common global search API for differing backends
    """
    def index(obj, attributes=None):
        """
        Index an object with backend API.

        :param obj: The Plone object to be indexed
        :type obj: A Plone object
        :param attributes: Optional list of attributes to index from the object
        :type attributes: `list`
        """

    def query(keywords, facets=None, start_date=None, end_date=None, start=0,
              step=None):
        """
        Perform query against the backend with given keywords and optional
        facet choices.

        Facets parameter must be given as a dictionary keyed on facet name with
        value being a list of chosen values for that facet.

        :param keywords: The keywords to search for
        :type keywords: str
        :param facets: The facets to filter results by
        :type facets: dict
        :param start_date: Earliest created date for results
        :type start_date: datetime.datetime
        :param end_date: Most recent created date for results
        :type end_date: datetime.datetime
        :param start: The offset position in results to start from
        :type start: int
        :param step: The maximum number of results to return
        :type step: int
        :returns: The results as a `SearchResponse` object
        :rtype: `SearchResponse`
        """


class ISearchResult(Interface):
    """
    Interface defining an individual search result
    """
    title = Attribute(_(u'The title of the indexed document'))
    description = Attribute(_(u'The description of the indexed document'))
    path = Attribute(_(u'The relative path to the canonical document'))
    preview_image_path = Attribute(
        _(u'The relative path to the stored preview image of the canonical '
          u'document'))
    document_type = Attribute(
        _(u'The type of content contained in the indexed document'))
    highlighted_summary = Attribute(
        _(u'A highlighted summary provided by the backend'))
    url = Attribute(
        _(u'The absolute URL of the indexed document '
          u'based on the path and the host in the current request'))
    preview_image_url = Attribute(
        _(u'The absolute URL for a preview image '
          u'generated for the indexed document'))


class ISearchResponse(Interface):
    """
    Interface defining a common response object
    parsed from search engine backend
    :ivar results: An iterable of ISearchResult objects
    :ivar spell_corrected_search: The search string with any spelling
        corrections replaced
    :ivar: facets: A dictionary keyed on facet field names with values of the
        list of available values for each facet
    :ivar total_results: Count of the total results matching the search query
    """
    results = Attribute(_(u'The SearchResults returned from a query'))
    spell_corrected_search = Attribute(_(u'Spell corrected search string'))
    facets = Attribute(_(u'A dictionary of facets and available values'))
    total_results = Attribute(
        _(u'The total number of results generated from the query'))
