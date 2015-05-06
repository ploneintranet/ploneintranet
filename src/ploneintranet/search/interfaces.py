""" Interfaces for search API
"""
from zope.interface import Interface


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

    def query(keywords, facets=None, start=0, step=None):
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
        :param step: The maximum number of results to return
        :type step: int
        :returns: The results as a `SearchResponse` object
        :rtype: `SearchResponse`
        """
