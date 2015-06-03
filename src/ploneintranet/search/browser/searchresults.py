from Products.Five import BrowserView
from zope.component import getUtility

from datetime import datetime
from datetime import timedelta
from ..interfaces import ISiteSearch

SUPPORTED_FACETS = ['friendly_type_name', 'Subject']


class SearchResultsView(BrowserView):

    def _daterange_from_string(self, range_name, now=None):
        """
        Convert from range strings used in the template
        to actual datetimes
        """
        if now is None:
            now = datetime.now()
        start_of_today = now.replace(hour=0, minute=0, second=0)
        start = None
        end = None
        if range_name == 'today':
            start = start_of_today
            end = now
        elif range_name == 'last-week':
            start = start_of_today - timedelta(days=7)
            end = now
        elif range_name == 'last-month':
            start = start_of_today - timedelta(days=28)
            end = now
        elif range_name == 'before-last-month':
            start = datetime.min
            end = start_of_today - timedelta(days=28)
        return start, end

    def search_response(self):
        """
        Takes options from the search page request
        and returns the relevant response from the backend
        """
        form = self.request.form
        facets = {}

        if form.get('SearchableText'):
            # This means that the main search form was submitted,
            # so we start a new keyword-only search
            keywords = form.get('SearchableText')
        elif form.get('SearchableText_faceted'):
            # This means that the facets were changed, so
            # we refine an existing search
            keywords = form.get('SearchableText_faceted')
            for facet in SUPPORTED_FACETS:
                if form.get(facet):
                    facets[facet] = form.get(facet)
        else:
            return []

        if form.get('created'):
            start, end = self._daterange_from_string(form.get('created'))
        else:
            start = None
            end = None

        search_util = getUtility(ISiteSearch, name='zcatalog')
        response = search_util.query(
            keywords,
            facets=facets,
            start_date=start,
            end_date=end,
        )
        return response
