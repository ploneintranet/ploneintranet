# coding=utf-8
from plone import api
from plone.memoize.view import memoize
from plone.memoize.view import memoize_contextless
from ploneintranet.layout.app import apps_container_id
from Products.Five import BrowserView
from zExceptions import NotFound


class BookmarkView(BrowserView):
    ''' A view aware about bookmarked objects
    '''

    @property
    @memoize
    def ploneintranet_network(self):
        ''' The ploneintranet_network tool
        '''
        return api.portal.get_tool('ploneintranet_network')

    @property
    @memoize
    def bookmarks(self):
        ''' The Bookmarks storage
        '''
        return self.ploneintranet_network._bookmarks

    @property
    @memoize
    def bookmarked(self):
        ''' The Bookmarked objects storage
        '''
        return self.ploneintranet_network._bookmarked

    @property
    def app(self):
        portal = api.portal.get()
        return getattr(portal, apps_container_id).bookmarks

    @property
    @memoize_contextless
    def app_url(self):
        return self.app.app_url()


class BookmarkActionView(BookmarkView):
    ''' A view that makes some action before rendering
    '''
    @memoize
    def is_ajax(self):
        ''' Check if we have an ajax call
        '''
        requested_with = self.request.environ.get('HTTP_X_REQUESTED_WITH')
        return requested_with == 'XMLHttpRequest'

    @property
    @memoize
    def iconified(self):
        ''' Check the request to serve the bookmark link iconifioed
        '''
        if self.buttonified:
            return False
        return bool(self.request.get('iconified'))

    @property
    @memoize
    def buttonified(self):
        ''' Check the request to serve the bookmark link iconifioed
        '''
        return bool(self.request.get('buttonified'))

    def disable_diazo(self):
        ''' Disable diazo if this is an ajax call
        '''
        self.request.response.setHeader('X-Theme-Disabled', '1')

    def action(self):
        ''' Do something if needed
        '''

    @property
    def bookmark_context(self):
        ''' This return the context we are lloking at
        (by the default self.context but is overridable fopr apps)
        '''
        return self.context

    def __call__(self):
        ''' Check if we can bookmark and render the template
        '''
        if self.is_ajax():
            self.disable_diazo()
        self.action()
        return super(BookmarkView, self).__call__()


class BookmarkAppActionView(BookmarkActionView):
    @property
    def app(self):
        ''' The requested app
        '''
        return self.request.get('app')

    @property
    def bookmark_context(self):
        ''' We are looking for a tile
        '''
        view = api.content.get_view(
            'apps.html',
            self.context,
            self.request,
        )
        for tile in view.tiles():
            if tile.path == self.app:
                return tile
        raise NotFound
