# -*- coding: utf-8 -*-
"""Interfaces for search API."""
from zope.interface import Interface
from zope import schema

from ploneintranet.core import ploneintranetCoreMessageFactory as _  # noqa


class IPloneintranetSearchLayer(Interface):
    """Marker interface that defines a Zope 3 browser layer."""


class ISiteSearch(Interface):
    """Defines a common API for a site search utility."""

    def query(phrase=None,
              filters=None,
              start_date=None,
              end_date=None,
              start=0,
              step=None):
        """Perform a query with the given `phrase` and options.

        At least one of 'phrase' or 'filters' must be provided.

        `filters` parameter must be given as a mapping keyed on
        filter name with values being a list of chosen values for that filter.
        Valid filter keys are configured in registry record
        `ploneintranet.search.filter_fields`. By default the following filters
        are available: tags, friendly_type_name, portal_type, path.

        :param phrase: The phrase to search for.
        :type phrase: str
        :param filters: A mapping of names and values to filter results by.
        :type filters: dict
        :param start_date: Earliest modified date for results.
        :type start_date: datetime.datetime
        :param end_date: Most recent modified date for results.
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

    title = schema.TextLine(title=_(u'The title of this search result'))

    description = schema.TextLine(
        title=_(u'The description of this search result'))

    contact_email = schema.TextLine(
        title=_(u'A contact email address for this search result'))

    contact_telephone = schema.TextLine(
        title=_(u'The description of this search result'))

    portal_type = schema.TextLine(
        title=_(u'The portal type of this search result'))

    friendly_type_name = schema.TextLine(
        title=_(u'The friendly label for the type of search result'))

    highlighted_summary = schema.Text(
        title=_(u'A highlighted summary of this search result'))

    preview_image_path = schema.ASCIILine(
        title=_(u'The relative path to a preview image'
                u'representing this search result'))

    preview_image_url = schema.ASCIILine(
        title=_(u'The absolute URL for a preview image '
                u'representing search result'))

    path = schema.ASCIILine(
        title=_(u'The relative path to the content for this search result'))

    url = schema.ASCIILine(
        title=_(u'The absolute URL to the content for this search result '
                u'based on the path and the host in the current request'))


class ISearchResponse(Interface):
    """Defines a common API for search query responses."""

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
