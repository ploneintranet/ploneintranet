from Products.Five import BrowserView
from ploneintranet.search.results import SearchResponse
import random


class SearchResultsView(BrowserView):

    def results(self):
        fakeresults = []
        response = SearchResponse(fakeresults)
        response.total_results = random.randint(50, 100)
        return response
