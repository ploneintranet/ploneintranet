# coding=utf-8
from plone import api
from plone.memoize.view import memoize
from ploneintranet.search.browser.searchresults import SearchResultsView


class UserSearchView(SearchResultsView):
    ''' The search in the context of the user
    '''
    autoload_source = '#search-result'

    @property
    @memoize
    def results_macro(self):
        ''' Reuse the same markup from the base search
        '''
        view = api.content.get_view(
            'search',
            api.portal.get(),
            self.request
        )
        return view.index.macros.template['result_items']

    def is_searching(self):
        ''' Return all the results
        even if we do not submit any SearchableText,
        otherwise we will have a blank page
        '''
        return True
