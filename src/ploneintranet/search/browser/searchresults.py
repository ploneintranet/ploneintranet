from Products.Five import BrowserView
from zope.component import getUtility

from datetime import datetime
from datetime import timedelta
from ..interfaces import ISiteSearch

SUPPORTED_FILTERS = ['friendly_type_name', 'Subject']


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
        form = self.request.form
        filters = {}
        start = None
        end = None

        if form.get('SearchableText'):
            # This means that the main search form was submitted,
            # so we start a new keyword-only search
            keywords = form.get('SearchableText')
        elif form.get('SearchableText_filtered'):
            # This means that the filters were changed, so
            # we refine an existing search
            keywords = form.get('SearchableText_filtered')
            for filt in SUPPORTED_FILTERS:
                if form.get(filt):
                    filters[filt] = form.get(filt)
            if form.get('created'):
                start, end = self._daterange_from_string(form.get('created'))
        else:
            return []

        search_util = getUtility(ISiteSearch)
        response = search_util.query(
            keywords,
            filters=filters,
            start_date=start,
            end_date=end,
        )
        return response

    def search_by_type(self, type_name):
        """
        Search for specific content types
        """
        form = self.request.form
        keywords = form.get('SearchableText')
        filters = {'portal_type': type_name}

        search_util = getUtility(ISiteSearch)
        response = search_util.query(
            keywords,
            filters=filters,
        )
        return response

    def search_images(self):
        return self.search_by_type('Image')

    def search_files(self):
        return self.search_by_type('File')
