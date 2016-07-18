# coding=utf-8
from collections import defaultdict
from plone import api
from plone.memoize import forever
from plone.memoize.view import memoize
from ploneintranet.bookmarks.browser.base import BookmarkView
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.search.interfaces import ISiteSearch
from zope.component import getUtility


class View(BookmarkView):
    ''' The view for this app
    '''
    document_types = [
        'Document', 'File', 'Image'
    ]

    @property
    def workspace_types(self):
        return [
            portal_type for portal_type
            in api.portal.get_registry_record(
                'ploneintranet.workspace.workspace_type_filters'
            )
        ]

    def is_bookmarked(self, uid):
        ''' Check if an object is bookmarked by uid
        '''
        return self.ploneintranet_network.is_bookmarked('content', uid)

    @memoize
    def my_bookmarks(self):
        ''' Lookup all the bookmarks
        '''
        search_util = getUtility(ISiteSearch)
        uids = list(self.ploneintranet_network.get_bookmarks('content'))
        if not uids:
            return []
        response = search_util.query(
            self.request.get('SearchableText', ''),
            filters={
                'UID': uids,
            },
            step=9999,
        )
        return tuple(response)

    def get_first_letter(self, word):
        word = word.strip()
        if not word:
            return _('No title')
        letter = word[0].upper()
        if isinstance(letter, unicode):
            letter = letter.encode('utf8')
        return letter

    @memoize
    def my_bookmarks_by_letter(self):
        ''' Get all the bookmarked objects grouped by first letter
        '''
        items = defaultdict(list)
        for result in self.my_bookmarks():
            items[self.get_first_letter(result.title)].append(result)
        query = self.request.get('SearchableText', '').lower()
        for result in self.my_bookmarked_apps():
            title = self.context.translate(result.title)
            if query in title.lower():
                items[self.get_first_letter(title)].append(result)
        return items

    @memoize
    def my_bookmarks_grouped(self):
        ''' Get all the bookmarked objects grouped
        '''
        return self.my_bookmarks_by_letter()

    @memoize
    def my_bookmarks_sorted_groups(self):
        ''' The groups of my partition sorted
        '''
        if self.request.get('by_date'):
            return [
                _('Today'),
                _('Last week'),
                _('Last month'),
                _('All time'),
            ]
        groups = sorted(self.my_bookmarks_by_letter().keys())
        if _('No title') in groups:
            no_title = groups.pop(groups.index(_('No title')))
            groups.append(no_title)
        return groups

    @forever.memoize
    def friendly_type_to_icon_class(self, type_name):
        ''' Convert the friendly_type_name of the search results
        into an css class

        For the time being reuse the search one
        '''
        view = api.content.get_view(
            'search',
            self.context,
            self.request,
        )
        search_class = view.get_facet_type_class(type_name)
        return search_class.replace('type-', 'icon-file-', 1).replace(
            'icon-file-rich', 'icon-doc-text'
        )

    @property
    @memoize
    def apps_view(self):
        ''' Return the apps view
        '''
        return api.content.get_view(
            'apps.html',
            api.portal.get(),
            self.request,
        )

    @memoize
    def my_bookmarked_apps(self):
        ''' Get all the bookmarked apps
        '''

        ng = self.ploneintranet_network
        return [
            tile for tile in self.apps_view.tiles()
            if tile.path and ng.is_bookmarked('apps', tile.path)
        ]

    @memoize
    def my_bookmarked_workspaces(self):
        ''' Get all the bookmarked workspaces
        '''
        search_util = getUtility(ISiteSearch)
        uids = list(self.ploneintranet_network.get_bookmarks('content'))
        if not uids:
            return []
        response = search_util.query(
            filters={
                'UID': uids,
                'portal_type': self.workspace_types,
            },
            step=9999,
        )
        return tuple(response)

    @memoize
    def my_bookmarked_documents(self):
        ''' Get all the bookmarked documents
        '''
        search_util = getUtility(ISiteSearch)
        uids = list(self.ploneintranet_network.get_bookmarks('content'))
        if not uids:
            return []
        response = search_util.query(
            filters={
                'UID': uids,
                'portal_type': self.document_types,
            },
            step=9999,
        )
        return tuple(response)
