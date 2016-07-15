from collections import defaultdict
from datetime import date
from plone import api
from plone.memoize import forever
from plone.memoize.view import memoize
from plone.tiles import Tile
from ploneintranet.search.interfaces import ISiteSearch
from quaive.app.taxonomy import _
from zope.component import getUtility

import logging

log = logging.getLogger(__name__)


class GroupedSearchTile(Tile):

    # List of excluded portal_types
    _types_not_to_search_for = {
        'Folder',
        'Plone Site',
        'TempFolder',
        'ploneintranet.library.app',
        'ploneintranet.library.folder'
        'ploneintranet.library.section',
        'ploneintranet.userprofile.userprofile',
        'ploneintranet.userprofile.userprofilecontainer',
        'ploneintranet.workspace.workspacecontainer',
        'ploneintranet.workspace.workspacefolder',
        'todo',
    }

    @memoize
    def search_results(self):
        search_util = getUtility(ISiteSearch)
        pt = api.portal.get_tool('portal_types')
        types = [
            t for t in pt.keys() if t not in self._types_not_to_search_for
        ]
        response = search_util.query(
            filters={
                'Creator': self.context.getId(),
                'portal_type': types,
            },
            step=9999,
        )
        return response

    @memoize
    def results_by_date(self):
        ''' Return the list of results grouped by date
        '''
        docs = defaultdict(list)
        today = date.today()

        for result in self.search_results():
            if hasattr(result.modified, 'date'):
                day_past = (today - result.modified.date()).days
            else:
                day_past = 100
            if day_past < 1:
                docs[_('Today')].append(result)
            elif day_past < 7:
                docs[_('Last week')].append(result)
            elif day_past < 30:
                docs[_('Last month')].append(result)
            else:
                docs[_('All time')].append(result)
        return docs

    @memoize
    def results_by_letter(self):
        ''' Return the list of results grouped by letter
        '''
        docs = defaultdict(list)
        for result in self.search_results():
            stripped_title = result.title.strip()
            if stripped_title:
                key = stripped_title[0].upper()
                if isinstance(key, unicode):
                    key = key.encode('utf8')
            else:
                _('No title')
            docs[key].append(result)
        return docs

    @memoize
    def results_sorted_groups(self):
        ''' Return the groups
        '''
        group_by = self.request.get('group-by', 'first-letter')
        if group_by == 'first-letter':
            groups = sorted(self.results_by_letter().keys())
            if _('No title') in groups:
                no_title = groups.pop(groups.index(_('No title')))
                groups.append(no_title)
                return groups
        elif group_by == 'date':
            return [
                _('Today'),
                _('Last week'),
                _('Last month'),
                _('All time'),
            ]

    @memoize
    def results_grouped(self):
        ''' Dispatch to the relevant method to group the results
        '''
        group_by = self.request.get('group-by', 'first-letter')
        if group_by == 'first-letter':
            return self.results_by_letter()
        elif group_by == 'date':
            return self.results_by_date()

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
