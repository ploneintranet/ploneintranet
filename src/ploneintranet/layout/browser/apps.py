# coding=utf-8
from plone import api
from ploneintranet.layout.interfaces import IAppTile
from zope.component import getAdapters
from zope.publisher.browser import BrowserView


class AppNotAvailable(BrowserView):

    """ A nice not available page to be able to demo this beautifully
    """


class Apps(BrowserView):

    """ A view to serve as overview over apps
    """

    tile_interface = IAppTile

    def tiles(self):
        """
        list available tiles
        """
        tiles = [
            tile for name, tile in getAdapters([self.context], IAppTile)
        ]
        tiles.sort(key=lambda x: x.sorting_key)
        return tiles

    def get_bookmark_link(self, app):
        ''' Gets the app bookmark icon
        '''
        view = api.content.get_view(
            'bookmark-link-iconified',
            app,
            self.request
        )
        return view()
