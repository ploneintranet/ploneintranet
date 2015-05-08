from datetime import datetime
from plone import api
from plone.batching import Batch
from zope.interface import implements
from zope.globalrequest import getRequest
from zope.component import adapts
from Products.ZCatalog.interfaces import ICatalogBrain

from .interfaces import ISiteSearch
from .interfaces import ISearchResult, ISearchResponse


class ZCatalogSearchResult(object):
    """
    Adapts a catalog brain to a search result
    """
    implements(ISearchResult)
    adapts(ICatalogBrain)

    title = None
    description = None
    path = None
    preview_image_path = None
    document_type = None
    highlighted_summary = None

    def __init__(self, brain):
        self._brain = brain
        self.title = brain['Title']
        self.path = brain.getPath()
        self.description = brain['Description']
        self.document_type = brain['friendly_type_name']
        if brain['has_thumbs']:
            self.preview_image_path = '{.path}/docconv_image_thumb.jpg'.format(
                self)

    def _path_to_url(self, physical_path):
        """
        Generate an absolute url from a physical path
        """
        if physical_path is not None:
            request = getRequest()
            return request.physicalPathToURL(physical_path)
        else:
            return None

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
        if self._brain['portal_type'] in view_types:
            url = '{0}/view'.format(url)
        return url

    @property
    def preview_image_url(self):
        """
        Generate the absolute URL for the preview image of the indexed document
        :return: The absolute URL to the preview image
        :rtype: str
        """
        return self._path_to_url(self.preview_image_path)


class ZCatalogSearchResponse(object):
    """
    Adapts a batched catalog search to a search response
    """
    adapts(Batch)
    implements(ISearchResponse)

    results = None
    spell_corrected_search = None
    facets = None
    total_results = None

    def __init__(self, batched_results):
        all_results = batched_results._sequence
        self.results = (ISearchResult(result) for result in batched_results)
        self.total_results = batched_results.sequence_length
        self.facets = {
            'friendly_type_name': {x['friendly_type_name']
                                   for x in all_results},
            'Subject': {y for x in all_results for y in x['Subject']},
        }


class ZCatalogSiteSearch(object):
    """
    Example implementation of ISiteSearch using the Plone catalog
    """
    implements(ISiteSearch)

    def index(self, obj, attributes=None):
        """
        Plone catalog already indexes the objects
        """
        pass

    def query(self, keywords, facets=None, start_date=datetime.min,
              end_date=datetime.max, start=0, step=None):
        """
        Query the catalog using passing facets as kwargs
        and keywords against SearchableText.

        Also limit the search by the date range given by start_date and
        end_date

        :param keywords: The string to pass to SearchableText
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
        if facets is None:
            facets = {}
        if step is None:
            step = 100
        catalog = api.portal.get_tool('portal_catalog')
        date_range_query = {'query': (start_date, end_date),
                            'range': 'min:max'}

        facets.update({
            'SearchableText': keywords,
            'created': date_range_query
        })
        brains = catalog.searchResults(facets)
        batch = Batch(brains, step, start)

        return ISearchResponse(batch)
