# -*- coding: utf-8 -*-
'''Setup/installation tests for this package.'''
from DateTime import DateTime
from plone import api
from plone.app.testing.interfaces import SITE_OWNER_NAME
from plone.testing import z2
from ploneintranet.bookmarks.browser.interfaces import IPloneintranetBookmarksLayer  # noqa
from ploneintranet.bookmarks.testing import FunctionalTestCase
from ploneintranet.layout.interfaces import IAppTile
from zope.component import getAdapter
from zope.interface import alsoProvides

PROJECTNAME = 'ploneintranet.bookmarks'


class TestViews(FunctionalTestCase):
    '''Test installation of this  product into Plone.'''

    def setUp(self):
        '''Custom shared utility setup for tests.'''
        self.portal = self.layer['portal']
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

    def login_as_portal_owner(self):
        """
        helper method to login as site admin
        """
        z2.login(self.layer['app']['acl_users'], SITE_OWNER_NAME)

    def get_request(self, params={}):
        ''' Prepare a fresh request
        '''
        request = self.request.clone()
        request.form.update(params)
        alsoProvides(request, IPloneintranetBookmarksLayer)
        return request

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
        app = getAdapter(self.portal, interface=IAppTile, name='bookmarks')
        output = api.content.get_view(
            'bookmark-link-iconified', app, self.get_request()
        )()
        self.assertIn(u'iconified=True', output)
        self.assertIn(
            u'icon iconified pat-inject icon-bookmark-empty',
            output
        )
        pn = api.portal.get_tool('ploneintranet_network')
        pn.bookmark('apps', app.path)
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

    def test_bookmark_app(self):
        ''' Test we can bookmark an app by calling a view
        '''
        pn = api.portal.get_tool('ploneintranet_network')
        app = getAdapter(self.portal, interface=IAppTile, name='bookmarks')
        self.assertFalse(pn.is_bookmarked('apps', app.path))
        view = api.content.get_view(
            'bookmark-app', self.portal, self.get_request({
                'app': app.path,
                'iconified': True,
            })
        )
        view()
        self.assertTrue(pn.is_bookmarked('apps', app.path))

    def test_unbookmark_app(self):
        ''' Test we can unbookmark an object by calling a view
        '''
        pn = api.portal.get_tool('ploneintranet_network')
        app = getAdapter(self.portal, interface=IAppTile, name='bookmarks')
        pn.bookmark('apps', app.path)
        self.assertTrue(pn.is_bookmarked('apps', app.path))
        view = api.content.get_view(
            'unbookmark-app', self.portal, self.get_request({
                'app': app.path,
                'iconified': True,
            })
        )
        view()
        self.assertFalse(pn.is_bookmarked('apps', app.path))

    def test_app_bookmarks(self):
        ''' Test app_bookmarks
        '''
        view = api.content.get_view(
            'app-bookmarks', self.portal, self.get_request()
        )

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
            [x for x in view.my_bookmarked_workspaces()],
            [],
        )
        self.assertListEqual(
            [x for x in view.my_bookmarks_by_letter()],
            []
        )

        # Then we bookmark some contents and the application
        ws = self.portal['workspaces']['bookmarkable-workspace']
        page = self.portal['bookmarkable-page']
        app = getAdapter(self.portal, interface=IAppTile, name='bookmarks')
        view.ploneintranet_network.bookmark('content', ws.UID())
        view.ploneintranet_network.bookmark('content', page.UID())
        view.ploneintranet_network.bookmark('apps', app.path)

        # And the view starts to get crowded
        view = api.content.get_view(
            'app-bookmarks', self.portal, self.get_request()
        )

        self.assertListEqual(
            [x.title for x in view.my_bookmarks()],
            ['Bookmarkable page', 'Bookmarkable workspace', u'bookmarks']
        )
        self.assertListEqual(
            view.my_bookmarks_sorted_groups(),
            ['B']
        )
        self.assertListEqual(
            sorted([x.title for x in view.my_bookmarks_grouped()['B']]),
            ['Bookmarkable page', 'Bookmarkable workspace', u'bookmarks']
        )
        self.assertListEqual(
            sorted([x.title for x in view.my_bookmarked_workspaces()]),
            ['Bookmarkable workspace'],
        )

        # And let's filter by date
        view = api.content.get_view(
            'app-bookmarks', self.portal, self.get_request({
                'group_by': 'created'
            })
        )
        self.assertListEqual(
            view.my_bookmarks_sorted_groups(),
            [u'Today', u'Last week', u'Last month', u'All time']
        )
        self.assertListEqual(
            [x.title for x in view.my_bookmarks_grouped()[u'Today']],
            ['Bookmarkable page'],
        )
        self.assertListEqual(
            [x.title for x in view.my_bookmarks_grouped()[u'All time']],
            ['Bookmarkable workspace', u'bookmarks']
        )

        # And let's filter by workspace
        view = api.content.get_view(
            'app-bookmarks', self.portal, self.get_request({
                'group_by': 'workspace'
            })
        )
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
            ['Bookmarkable page', u'bookmarks'],
        )

        # Of course we can even apply filters together
        # And let's filter by workspace
        view = api.content.get_view(
            'app-bookmarks', self.portal, self.get_request({
                'SearchableText': 'bookmarkable',
                'group_by': 'created'
            })
        )
        self.assertListEqual(
            [x.title for x in view.my_bookmarks_grouped()[u'All time']],
            ['Bookmarkable workspace']
        )

    def test_app_bookmarks_search(self):
        ''' Test app_bookmarks
        '''
        # We bookmark some contents and the application
        pn = api.portal.get_tool('ploneintranet_network')
        ws = self.portal['workspaces']['bookmarkable-workspace']
        page = self.portal['bookmarkable-page']
        app = getAdapter(self.portal, interface=IAppTile, name='bookmarks')
        pn.bookmark('content', ws.UID())
        pn.bookmark('content', page.UID())
        pn.bookmark('apps', app.path)

        # With no search parameter everything is return
        view = api.content.get_view(
            'app-bookmarks', self.portal, self.get_request({
                'SearchableText': '',
            })
        )
        self.assertListEqual(
            sorted([x.title for x in view.my_bookmarks_grouped()['B']]),
            ['Bookmarkable page', 'Bookmarkable workspace', u'bookmarks']
        )
        # but we can filter contents
        view = api.content.get_view(
            'app-bookmarks', self.portal, self.get_request({
                'SearchableText': 'workSpace',
            })
        )
        self.assertListEqual(
            sorted([x.title for x in view.my_bookmarks_grouped()['B']]),
            ['Bookmarkable workspace']
        )
        # or the application
        view = api.content.get_view(
            'app-bookmarks', self.portal, self.get_request({
                'SearchableText': 'bookMarks',
            })
        )
        self.assertListEqual(
            sorted([x.title for x in view.my_bookmarks_grouped()['B']]),
            [u'bookmarks']
        )
