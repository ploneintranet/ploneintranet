# coding=utf-8
from plone import api
from plone.memoize.view import memoize_contextless
from plone.tiles import Tile


class BookmarksTile(Tile):
    '''Bookmarks as a tile'''

    @property
    @memoize_contextless
    def app_bookmarks(self):
        ''' Return the bookmark that will be displayed in the tile
        '''
        return api.content.get_view(
            'app-bookmarks',
            api.portal.get(),
            self.request,
        )
