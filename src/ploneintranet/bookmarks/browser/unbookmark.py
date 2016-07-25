# coding=utf-8
from AccessControl import Unauthorized
from ploneintranet.bookmarks.browser.base import BookmarkActionView
from ploneintranet.bookmarks.browser.base import BookmarkAppActionView
from plone import api


class View(BookmarkActionView):
    ''' The view for unbookmarking content
    '''
    def action(self):
        ''' Check if we can bookmark this view
        '''
        if api.user.is_anonymous():
            raise Unauthorized
        self.ploneintranet_network.unbookmark('content', self.context.UID())


class AppView(BookmarkAppActionView):
    ''' The view for unbookmarking apps
    '''
    def action(self):
        ''' Unbookmark the requested app
        '''
        if api.user.is_anonymous():
            raise Unauthorized
        self.ploneintranet_network.unbookmark(
            'apps', self.request.get('app', '')
        )
