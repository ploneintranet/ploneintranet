# coding=utf-8
from plone import api
from plone.memoize.view import memoize_contextless
from plone.tiles import Tile
from ploneintranet.layout.app import apps_container_id
from ploneintranet.bookmarks.browser.base import BookmarkActionView
from ploneintranet.bookmarks.browser.bookmark_link import View
from ploneintranet.core import ploneintranetCoreMessageFactory as _  # noqa
from plone.protect.utils import addTokenToUrl


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

    @memoize_contextless
    def get_bookmarks(self):
        ''' Return the bookarms accoring to the requested sort_by
        '''
        sort_by = self.request.get('sort_by', 'recent')
        if sort_by == 'popularity':
            return self.app_bookmarks.most_popular_bookmarks()
        else:
            return self.app_bookmarks.my_recent_bookmarks()


class WorkspaceBookmarkTile(Tile, BookmarkActionView, View):
    """ Proto specific way to bookmark a workspace on the workspace view """
    msg = ''

    def __call__(self):

        if self.request.get('bookmark'):
            self.ploneintranet_network.bookmark('content', self.context.UID())
            self.msg = _(u'success_bookmark',
                         u'You have bookmarked this item.')
        elif self.request.get('unbookmark'):
            self.ploneintranet_network.unbookmark('content',
                                                  self.context.UID())
            self.msg = _(u'success_unbookmarked',
                         u'You have unbookmarked this item.')

        if self.is_bookmarked:
            self.title = 'Bookmarked'
            self.icon_class = 'icon-bookmark'
            self.description = \
                _(u'Remove this workspace from your bookmarks')
            self.link = addTokenToUrl(self.url + '?unbookmark=1')
        else:
            self.title = 'Bookmark'
            self.icon_class = 'icon-bookmark-empty'
            self.description = \
                _(u'Add this workspace to your bookmarks.')
            self.link = addTokenToUrl(self.url + '?bookmark=1')
            self.status = ''
        return self.index()
