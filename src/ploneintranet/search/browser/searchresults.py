from Products.Five import BrowserView
from ZTUtils import make_query
from zope.component import getUtility

from datetime import datetime
from datetime import timedelta
from ..interfaces import ISiteSearch

SUPPORTED_FILTERS = ['friendly_type_name', 'Subject']
RESULTS_PER_PAGE = 10


class SearchResultsView(BrowserView):

    def _daterange_from_string(self, range_name, now=None):
        """
        Convert from range strings used in the template
        to actual datetimes
        """
        if now is None:
            now = datetime.now()
        start_of_today = now.replace(hour=0, minute=0, second=0)
        start_date = None
        end_date = None
        if range_name == 'today':
            start_date = start_of_today
            end_date = now
        elif range_name == 'last-week':
            start_date = start_of_today - timedelta(days=7)
            end_date = now
        elif range_name == 'last-month':
            start_date = start_of_today - timedelta(days=28)
            end_date = now
        elif range_name == 'before-last-month':
            start_date = datetime.min
            end_date = start_of_today - timedelta(days=28)
        return start_date, end_date

    def page_number(self):
        """Get current page number from the request"""
        try:
            page = int(self.request.form.get('page', 1))
        except ValueError:
            page = 1
        return page

    def next_page_number(self, total_results):
        """Get page number for next page of search results"""
        page = self.page_number()
        if page * RESULTS_PER_PAGE < total_results:
            return page + 1
        else:
            return None

    def next_page_url(self, total_results):
        """Get url for the next page of results"""
        next_page_number = self.next_page_number(total_results)
        if not next_page_number:
            return
        new_query = make_query(
            self.request.form.copy(),
            {'page': next_page_number}
        )
        return '{url}?{qs}'.format(
            url=self.request.ACTUAL_URL,
            qs=new_query
        )

    def preview_class(self, portal_type):
        """Get the matching preview class for a portal type"""
        if portal_type == 'ploneintranet.userprofile.userprofile':
            return 'user'
        else:
            return 'file'

    def search_response(self):
        form = self.request.form
        filters = {}
        start_date = None
        end_date = None

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
                start_date, end_date = self._daterange_from_string(
                    form.get('created')
                )
        else:
            return []

        start = (self.page_number() - 1) * RESULTS_PER_PAGE

        search_util = getUtility(ISiteSearch)
        response = search_util.query(
            keywords,
            filters=filters,
            start_date=start_date,
            end_date=end_date,
            start=start,
            step=RESULTS_PER_PAGE,
        )
        return response

    def search_by_type(self, type_name):
        """
        Search for specific content types
        """
        form = self.request.form
        keywords = form.get('SearchableText')
        if not keywords:
            return []
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

    def search_people(self):
        return self.search_by_type('ploneintranet.userprofile.userprofile')
