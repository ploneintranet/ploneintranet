# -*- coding: utf-8 -*-
"""Interfaces for search API."""
from zope.interface import Interface
from zope import schema

from . import _


class IPloneintranetSearchLayer(Interface):
    """Marker interface that defines a Zope 3 browser layer."""


class ISiteSearch(Interface):
    """Defines a common API for a site search utility."""

    def query(phrase,
              filters=None,
              start_date=None,
              end_date=None,
              start=0,
              step=None):
        """Perform a query with the given `phase` and options.

        `filters` parameter must be given as a mapping keyed on
        filter name with values being a list of chosen values for that filter.

        :param phrase: The phrase to search for.
        :type phrase: str
        :param filters: A mapping of names and values to filter results by.
        :type filters: dict
        :param start_date: Earliest created date for results.
        :type start_date: datetime.datetime
        :param end_date: Most recent created date for results.
        :type end_date: datetime.datetime
        :param start: The offset position in results to start from.
        :type start: int
        :param step: The maximum number of results to return.
        :type step: int
        :returns: The results as a `SearchResponse` object.
        :rtype: `SearchResponse`
        """


class ISearchResult(Interface):
    """Defines a common API for search results."""

    title = schema.TextLine(title=_(u'The title of the indexed document'))

    description = schema.TextLine(
        title=_(u'The description of the indexed document'))

    friendly_type_name = schema.TextLine(
        title=_(u'The friendly type name of content of the indexed document'))

    highlighted_summary = schema.Text(
        title=_(u'A highlighted summary provided by the backend'))

    preview_image_path = schema.ASCIILine(
        title=_(u'The relative path to the stored preview image of'
                u'the canonical document'))

    preview_image_url = schema.ASCIILine(
        title=_(u'The absolute URL for a preview image '
                u'generated for the indexed document'))

    path = schema.ASCIILine(
        title=_(u'The relative path to the canonical document'))

    url = schema.ASCIILine(
        title=_(u'The absolute URL of the indexed document '
                u'based on the path and the host in the current request'))


class ISearchResponse(Interface):
    """Defines a common API for search query responses.

    Iterating over this object will yield search result objects
    conforming to `ISearchResult`.

    :ivar spell_corrected_search: The search string with any spelling
        corrections replaced
    :ivar: facets: A dictionary keyed on facet field names with values of the
        list of available values for each facet
    :ivar total_results: Count of the total results matching the search query
    """

    spell_corrected_search = schema.TextLine(
        title=_(u'Spell corrected search string'))

    facets = schema.Dict(
        title=_(u'A dictionary of facets and available values'))

    total_results = schema.Int(
        title=_(u'The total number of results generated from the query'))

    def __iter__():
        """Search responses should implement the `Iterable` protocol.

        Iteratating over this object should yield search results.
        """
