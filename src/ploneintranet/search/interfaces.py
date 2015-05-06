""" Interfaces for search API
"""
from zope.interface import Interface, Attribute

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

    def query(keywords, facets=None, start=0, count=None):
        """
        Perform query against the backend with given keywords and optional
        facet choices.

        Facets parameter must be given as a dictionary keyed on facet name with
        value being a list of chosen values for that facet.

        :param keywords: The keywords to search for
        :type keywords: str
        :param facets: The facets to filter results by
        :type facets: dict
        :param start: The offset position in results to start from
        :type start: int
        :param count: The maximum number of results to return
        :type count: int
        :returns: The results as a `SearchResponse` object
        :rtype: `ISearchResponse`
        """


class ISearchResult(Interface):
    """
    Interface defining an individual search result
    :ivar fields: A dictionary keyed on indexed field name with value of the
        matching result for that field
    :ivar highlighted_summary: A string containing a summary of the resulting
        document with markup highlighting the matching keywords from the search
        query
    """
    fields = Attribute(_(u'A dictionary of indexed fields and their values'))
    highlighted_summary = Attribute(
        _(u'A highlighted summary provided by the backend'))


class ISearchResponse(Interface):
    """
    Interface defining a common response object
    parsed from search engine backend
    :ivar results: An iterable of ISearchResult objects
    :ivar did_you_mean: The search string with any spelling corrections
        replaced
    :ivar: facets: A dictionary keyed on facet field names with values of the
        list of available values for each facet
    :ivar total_results: Count of the total results matching the search query
    """
    results = Attribute(_(u'The SearchResults returned from a query'))
    did_you_mean = Attribute(_(u'Spell corrected search string'))
    facets = Attribute(_(u'A dictionary of facets and available values'))
    total_results = Attribute(
        _(u'The total number of results generated from the query'))
