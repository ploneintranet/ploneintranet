# coding=utf-8
from plone import api
from plone.memoize.view import memoize_contextless
from plone.tiles import Tile
from ploneintranet.layout.app import apps_container_id


class BookmarksTile(Tile):
    '''Bookmarks as a tile'''

    @property
    def app(self):
        portal = api.portal.get()
        return getattr(portal, apps_container_id).bookmarks

    @property
    @memoize_contextless
    def app_url(self):
        return self.app.absolute_url()

    @property
    @memoize_contextless
    def app_bookmarks(self):
        ''' Return the bookmark that will be displayed in the tile
        '''
        return api.content.get_view(
            'app-bookmarks',
            self.app,
            self.request,
        )
