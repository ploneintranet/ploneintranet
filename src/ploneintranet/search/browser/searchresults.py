from Products.Five import BrowserView
from zope.component import getUtility

from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil.relativedelta import MO
from ..interfaces import ISiteSearch

SUPPORTED_FACETS = ['friendly_type_name', 'Subject']


class SearchResultsView(BrowserView):

    def _daterange_from_string(self, range_name):
        """
        Convert from range strings used in the template
        to actual datetimes
        """
        now = datetime.now()
        start_of_today = now.replace(hour=0, minute=0)
        start = None
        end = None
        if range_name == 'today':
            start = start_of_today
            end = now
        elif range_name == 'yesterday':
            start = start_of_today - relativedelta(days=1)
            end = start_of_today
        elif range_name == 'this-week':
            start = start_of_today - relativedelta(weekday=MO(-1))
            end = now
        elif range_name == 'last-week':
            start = start_of_today - relativedelta(weekday=MO(-2))
            end = start_of_today - relativedelta(weekday=MO(-1))
        return start, end

    def search_response(self):
        form = self.request.form
        keywords = form.get('SearchableText')
        if not keywords:
            return None
        elif isinstance(keywords, list):
            # Template means that sometimes we get
            # multiple copies of the text input
            keywords = keywords[0]

        facets = {}
        for facet in SUPPORTED_FACETS:
            if form.get(facet):
                facets[facet] = form.get(facet)

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
