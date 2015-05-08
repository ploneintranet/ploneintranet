from Products.Five import BrowserView
from zope.component import getUtility

from ..interfaces import ISiteSearch

SUPPORTED_FACETS = ['friendly_type_name', 'Subject']


class SearchResultsView(BrowserView):

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

        search_util = getUtility(ISiteSearch, name='example')
        response = search_util.query(
            keywords=keywords,
            facets=facets,
        )
        return response
