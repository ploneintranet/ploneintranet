# coding=utf-8
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.layout.adapters.app_tiles import BaseTile


class BookmarkTile(BaseTile):
    key = 'bookmarks'
    title = _('bookmarks', 'Bookmarks')
    path = '@@app-bookmarks'
    position = 100
