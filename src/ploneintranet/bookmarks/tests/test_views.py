# -*- coding: utf-8 -*-
'''Setup/installation tests for this package.'''
from DateTime import DateTime
from plone import api
from plone.app.testing.interfaces import SITE_OWNER_NAME
from plone.testing import z2
from ploneintranet.bookmarks.browser.interfaces import IPloneintranetBookmarksLayer  # noqa
from ploneintranet.bookmarks.testing import FunctionalTestCase
from ploneintranet.layout.app import apps_container_id
from zope.interface import alsoProvides

PROJECTNAME = 'ploneintranet.bookmarks'


class TestViews(FunctionalTestCase):
    '''Test installation of this  product into Plone.'''

    def setUp(self):
        '''Custom shared utility setup for tests.'''
        self.portal = self.layer['portal']
        self.bookmark_app = self.portal.restrictedTraverse(
            '%s/bookmarks' % apps_container_id
        )
        self.request = self.layer['request']
        self.login_as_portal_owner()
        api.content.create(
            container=self.portal,
            type='Document',
            title='Bookmarkable page',
        )
        workspace = api.content.create(
            container=self.portal['workspaces'],
            type='ploneintranet.workspace.workspacefolder',
            title='Bookmarkable workspace',
        )
        workspace.creation_date = DateTime('2016/01/01')
        workspace.reindexObject(idxs=['created'])
        api.content.create(
            type='ploneintranet.userprofile.userprofile',
            container=self.portal.profiles,
            title='Bookmarkable One',
            first_name='Bookmarkable',
            last_name='One',
        )

    def login_as_portal_owner(self):
        """
        helper method to login as site admin
        """
        z2.login(self.layer['app']['acl_users'], SITE_OWNER_NAME)

    def bookmark_contents(self):
        app = self.bookmark_app
        page = self.portal['bookmarkable-page']
        person = self.portal.profiles['bookmarkable-one']
        ws = self.portal['workspaces']['bookmarkable-workspace']
        pn = api.portal.get_tool('ploneintranet_network')
        pn.bookmark('content', app.UID())
        pn.bookmark('content', page.UID())
        pn.bookmark('content', person.UID())
        pn.bookmark('content', ws.UID())
        bookmarked_on = pn._bookmarked_on[u'admin']
        # ws will result bookmarked two days ago
        bookmarked_on[ws.UID()] = (DateTime() - 2).asdatetime()
        # app will result bookmarked 100 days ago
        bookmarked_on[app.UID()] = (DateTime() - 100).asdatetime()

    def get_request(self, params={}):
        ''' Prepare a fresh request
        '''
        request = self.request.clone()
        request.form.update(params)
        alsoProvides(request, IPloneintranetBookmarksLayer)
        return request

    def get_app_bookmarks(self, params={}):
        ''' Get the app-bookmarks view called with params
        '''
        return api.content.get_view(
            'app-bookmarks',
            self.bookmark_app,
            self.get_request(params),
        )

    def test_bookmark_link_view_on_content(self):
        ''' Test the bookmark link view on a content
        '''
        page = self.portal['bookmarkable-page']
        view = api.content.get_view('bookmark-link', page, self.get_request())
        self.assertIn(
            u'Add this item to your bookmarks',
            view()
        )
        pn = api.portal.get_tool('ploneintranet_network')
        pn.bookmark('content', page.UID())
        view = api.content.get_view('bookmark-link', page, self.get_request())
        self.assertIn(
            u'Remove this item from your bookmarks',
            view()
        )

    def test_bookmark_link_iconified_view_on_app(self):
        ''' Test the bookmark link view on an app
        '''
        app = self.bookmark_app
        output = api.content.get_view(
            'bookmark-link-iconified', app, self.get_request()
        )()
        self.assertIn(u'iconified=True', output)
        self.assertIn(
            u'icon iconified pat-inject icon-bookmark-empty',
            output
        )
        pn = api.portal.get_tool('ploneintranet_network')
        pn.bookmark('content', app.UID())
        output = api.content.get_view(
            'bookmark-link-iconified', app, self.get_request()
        )()
        self.assertIn(u'iconified=True', output)
        self.assertIn(
            u'icon iconified pat-inject icon-bookmark active',
            output
        )

    def test_bookmark_content(self):
        ''' Test we can bookmark an object by calling a view
        '''
        pn = api.portal.get_tool('ploneintranet_network')
        page = self.portal['bookmarkable-page']
        self.assertFalse(pn.is_bookmarked('content', page.UID()))
        view = api.content.get_view(
            'bookmark', page, self.get_request()
        )
        view()
        self.assertTrue(pn.is_bookmarked('content', page.UID()))

    def test_unbookmark_content(self):
        ''' Test we can unbookmark an object by calling a view
        '''
        pn = api.portal.get_tool('ploneintranet_network')
        page = self.portal['bookmarkable-page']
        pn.bookmark('content', page.UID())
        self.assertTrue(pn.is_bookmarked('content', page.UID()))
        view = api.content.get_view(
            'unbookmark', page, self.get_request()
        )
        view()
        self.assertFalse(pn.is_bookmarked('content', page.UID()))

    def test_bookmark_people(self):
        pn = api.portal.get_tool('ploneintranet_network')
        person = self.portal.profiles['bookmarkable-one']
        self.assertFalse(pn.is_bookmarked('content', person.UID()))
        view = api.content.get_view(
            'bookmark', person, self.get_request()
        )
        view()
        self.assertTrue(pn.is_bookmarked('content', person.UID()))

    def test_unbookmark_people(self):
        pn = api.portal.get_tool('ploneintranet_network')
        person = self.portal.profiles['bookmarkable-one']
        pn.bookmark('content', person.UID())
        self.assertTrue(pn.is_bookmarked('content', person.UID()))
        view = api.content.get_view(
            'unbookmark', person, self.get_request()
        )
        view()
        self.assertFalse(pn.is_bookmarked('content', person.UID()))

    def test_app_bookmarks(self):
        ''' Test app_bookmarks
        '''
        view = self.get_app_bookmarks()

        self.assertListEqual(
            [x.title for x in view.my_bookmarks()],
            []
        )
        self.assertListEqual(
            [x for x in view.my_bookmarks_grouped()],
            []
        )
        self.assertListEqual(
            [x for x in view.my_bookmarks_sorted_groups()],
            []
        )
        self.assertListEqual(
            [x for x in view.my_bookmarked_people()],
            [],
        )
        self.assertListEqual(
            [x for x in view.my_bookmarked_workspaces()],
            [],
        )
        self.assertListEqual(
            [x for x in view.my_bookmarks_by_letter()],
            []
        )

        # Then we bookmark some contents and the application
        self.bookmark_contents()

        # And the view starts to get crowded
        view = self.get_app_bookmarks()

        self.assertListEqual(
            [x.title for x in view.my_bookmarks()],
            [
                'Bookmarkable One',
                'Bookmarkable page',
                'Bookmarkable workspace',
                'Bookmarks',
            ],
        )

    def test_app_bookmarks_grouped_by_letter(self):
        self.bookmark_contents()
        view = self.get_app_bookmarks()
        self.assertListEqual(
            view.my_bookmarks_sorted_groups(),
            ['B']
        )
        self.assertListEqual(
            sorted([x.title for x in view.my_bookmarks_grouped()['B']]),
            [
                'Bookmarkable One',
                'Bookmarkable page',
                'Bookmarkable workspace',
                'Bookmarks',
            ],
        )
        self.assertListEqual(
            sorted([x.title for x in view.my_bookmarked_workspaces()]),
            ['Bookmarkable workspace'],
        )

    def test_app_bookmarks_grouped_by_date(self):
        self.bookmark_contents()
        # And let's filter by date
        view = self.get_app_bookmarks({
            'group_by': 'created',
        })
        self.assertListEqual(
            view.my_bookmarks_sorted_groups(),
            [u'Today', u'Last week', u'Last month', u'All time']
        )
        self.assertListEqual(
            [x.title for x in view.my_bookmarks_grouped()[u'Today']],
            [
                'Bookmarkable One',
                'Bookmarkable page',
                'Bookmarks',
            ],
        )
        self.assertListEqual(
            [x.title for x in view.my_bookmarks_grouped()[u'All time']],
            ['Bookmarkable workspace'],
        )

    def test_app_bookmarks_grouped_by_workspace(self):
        self.bookmark_contents()
        # And let's filter by workspace
        view = self.get_app_bookmarks({
            'group_by': 'workspace',
        })
        self.assertListEqual(
            view.my_bookmarks_sorted_groups(),
            [u'Bookmarkable workspace', u'Not in a workspace']
        )
        self.assertListEqual(
            [
                x.title
                for x in view.my_bookmarks_grouped()[u'Bookmarkable workspace']
            ],
            ['Bookmarkable workspace']
        )
        self.assertListEqual(
            [
                x.title
                for x in view.my_bookmarks_grouped()[u'Not in a workspace']
            ],
            [
                'Bookmarkable One',
                'Bookmarkable page',
                'Bookmarks',
            ],
        )

    def test_app_bookmarks_grouped_by_bookmarked(self):
        self.bookmark_contents()
        view = self.get_app_bookmarks({
            'group_by': 'bookmarked',
        })
        self.assertListEqual(
            view.my_bookmarks_sorted_groups(),
            [u'Today', u'Last week', u'Last month', u'All time']
        )
        bookmarks_grouped = view.my_bookmarks_grouped()
        self.assertListEqual(
            [x.title for x in bookmarks_grouped[u'Today']],
            [
                'Bookmarkable One',
                'Bookmarkable page',
            ],
        )
        self.assertListEqual(
            [x.title for x in bookmarks_grouped[u'Last week']],
            [
                'Bookmarkable workspace',
            ],
        )
        self.assertListEqual(
            [x.title for x in bookmarks_grouped[u'All time']],
            [
                'Bookmarks',
            ],
        )

    def test_app_bookmarks_search(self):
        ''' Test app_bookmarks
        '''
        # We bookmark some contents and the application
        self.bookmark_contents()

        # With no search parameter everything is returned
        view = self.get_app_bookmarks({
            'SearchableText': '',
        })
        self.assertListEqual(
            sorted([x.title for x in view.my_bookmarks_grouped()['B']]),
            [
                'Bookmarkable One',
                'Bookmarkable page',
                'Bookmarkable workspace',
                'Bookmarks',
            ]
        )
        # but we can filter contents
        view = self.get_app_bookmarks({
            'SearchableText': 'workSpace',
        })
        self.assertListEqual(
            sorted([x.title for x in view.my_bookmarks_grouped()['B']]),
            ['Bookmarkable workspace']
        )
        # or the application
        view = self.get_app_bookmarks({
            'SearchableText': 'bookMarks',
        })
        self.assertListEqual(
            sorted([x.title for x in view.my_bookmarks_grouped()['B']]),
            ['Bookmarks']
        )

    def test_app_bookmarks_grouped_by_bookmarked_and_filtered(self):
        ''' We search and filter bookmarks
        '''
        self.bookmark_contents()
        view = self.get_app_bookmarks({
            'SearchableText': 'page',
            'group_by': 'bookmarked',
        })
        self.assertListEqual(
            [x.title for x in view.my_bookmarks_grouped()[u'Today']],
            [
                'Bookmarkable page',
            ]
        )

    def test_app_bookmarks_grouped_by_created_and_filtered(self):
        ''' We search and filter bookmarks
        '''
        self.bookmark_contents()
        view = self.get_app_bookmarks({
            'SearchableText': 'bookmarkable',
            'group_by': 'created'
        })
        self.assertListEqual(
            [x.title for x in view.my_bookmarks_grouped()[u'All time']],
            ['Bookmarkable workspace']
        )

    def test_app_bookmarks_grouped_by_workspace_and_filtered(self):
        ''' We search and filter bookmarks
        '''
        self.bookmark_contents()
        view = self.get_app_bookmarks({
            'SearchableText': 'bookmarkable',
            'group_by': 'workspace'
        })
        self.assertListEqual(
            [
                x.title
                for x in view.my_bookmarks_grouped()[u'Not in a workspace']
            ],
            [
                'Bookmarkable One',
                'Bookmarkable page',
            ]
        )

    def test_bookmarks_tile(self):
        ''' The bookmarks tile displays and filters the bookmarks
        '''
        tile = api.content.get_view(
            'bookmarks.tile',
            self.portal,
            self.get_request()
        )
        # we hav a tile that displays the bookmarks using the app-bookmarks
        self.assertTupleEqual(tile.app_bookmarks.my_bookmarks(), ())

        # We bookmark some contents and the application
        pn = api.portal.get_tool('ploneintranet_network')
        ws = self.portal['workspaces']['bookmarkable-workspace']
        page = self.portal['bookmarkable-page']
        app = self.bookmark_app
        pn.bookmark('content', ws.UID())
        pn.bookmark('content', page.UID())
        pn.bookmark('content', app.UID())

        # Let's cleanup the request to invalidate the cache
        tile.request = self.get_request()
        self.assertEqual(len(tile.app_bookmarks.my_bookmarks()), 3)

        # if we specify an id_suffix the tile will use it while rendering
        # to avoid collisions with other similar portlets.
        tile = api.content.get_view(
            'bookmarks.tile',
            self.portal,
            self.get_request({
                'id_suffix': 'zzz',
            })
        )
        page = tile()
        self.assertIn('id="portlet-bookmarkszzz"', page)
        self.assertIn('id="bookmarks-search-itemszzz"', page)
        self.assertIn('#bookmarks-search-itemszzz"', page)
        self.assertIn('id="portlet-bookmarks-bookmarks-listzzz"', page)
