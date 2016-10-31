# -*- coding: utf-8 -*-
import unittest2 as unittest
from datetime import datetime
from ploneintranet.network.graph import NetworkGraph
from ploneintranet.network.testing import IntegrationTestCase


class TestBookmarkContent(unittest.TestCase):

    def setUp(self):
        self.userid = 'testperson'
        self.object_uuid = '827e65bd826a89790eba679e0c9ff864'
        self.container = NetworkGraph()

    def _bookmark_content(self):
        self.container.bookmark("content", self.object_uuid, self.userid)

    def test_bookmark_content(self):
        self._bookmark_content()

        items = self.container.get_bookmarks("content", self.userid)
        self.assertListEqual(list(items), [self.object_uuid])

        users = self.container.get_bookmarkers("content", self.object_uuid)
        self.assertListEqual(sorted(list(users)), [self.userid])

    def test_bookmark_content_utf8(self):
        userid = u'M♥rÿ@test.org'
        self.container.bookmark("content", self.object_uuid, userid, )
        items = self.container.get_bookmarks("content", userid)
        self.assertListEqual(sorted(list(items)), [self.object_uuid])
        users = self.container.get_bookmarkers("content", self.object_uuid)
        self.assertListEqual(sorted(list(users)), [userid])

    def test_utf8_args(self):
        """BTree keys MUST be of type unicode. Check that the implementation
        enforces this."""
        g = NetworkGraph()
        with self.assertRaises(AttributeError):
            g.bookmark('content', 1, '2')
        with self.assertRaises(AttributeError):
            g.bookmark('content', '1', 2)
        with self.assertRaises(AttributeError):
            g.unbookmark('content', 1, '2')
        with self.assertRaises(AttributeError):
            g.unbookmark('content', '1', 2)
        with self.assertRaises(AttributeError):
            g.get_bookmarks('content', 1)
        with self.assertRaises(AttributeError):
            g.get_bookmarkers('content', 1)
        with self.assertRaises(AttributeError):
            g.is_bookmarked('content', 1, 2)

    def test_content_bookmarked_by_two_users(self):
        self._bookmark_content()
        self.container.bookmark("content", self.object_uuid, 'cyclon@test.org')

        items = self.container.get_bookmarks("content", self.userid)
        self.assertListEqual(sorted(list(items)), [self.object_uuid])
        items = self.container.get_bookmarks("content", 'cyclon@test.org')
        self.assertListEqual(sorted(list(items)), [self.object_uuid])

        users = self.container.get_bookmarkers("content", self.object_uuid)
        self.assertListEqual(
            sorted(list(users)),
            ['cyclon@test.org', self.userid]
        )

    def test_unbookmark_content(self):
        self._bookmark_content()
        self.container.unbookmark("content", self.object_uuid, self.userid)

        items = self.container.get_bookmarks("content", self.userid)
        self.assertListEqual(sorted(list(items)), [])

        users = self.container.get_bookmarkers("content", self.object_uuid)
        self.assertListEqual(sorted(list(users)), [])

    def test_get_content_bookmarks(self):
        self._bookmark_content()
        self.assertEqual(
            sorted(list(self.container.get_bookmarks("content", self.userid))),
            [self.object_uuid]
        )

    def test_get_content_bookmarks_empty(self):
        self.assertListEqual(
            self.container.get_bookmarks("content", self.userid),
            []
        )

    def test_is_content_bookmarked(self):
        self.assertFalse(
            self.container.is_bookmarked(
                "content", self.object_uuid, self.userid
            )
        )
        self._bookmark_content()
        self.assertTrue(
            self.container.is_bookmarked(
                "content", self.object_uuid, self.userid
            )
        )

    def test_get_content_bookmarkers(self):
        self._bookmark_content()
        self.assertIn(
            self.userid,
            self.container.get_bookmarkers("content", self.object_uuid)
        )

    def test_get_content_bookmarkers_empty(self):
        self.assertEqual(
            self.container.get_bookmarkers("content", self.object_uuid), []
        )


class TestBookmarkingDefaults(IntegrationTestCase):
    """Check fallbacks to currently logged in user."""

    def test_user_bookmark_unbookmark_content(self):
        g = NetworkGraph()
        g.bookmark('content', 'fake uuid')
        self.assertTrue(g.is_bookmarking('content', 'fake uuid'))
        self.assertIn('fake uuid', g.get_bookmarks('content'))
        g.unbookmark('content', 'fake uuid')
        self.assertFalse(g.is_bookmarking('content', 'fake uuid'))


class TestBookmarkTimestamps(IntegrationTestCase):
    """Check datetime storage of bookmarking actions"""

    def test_bookmark_sets_timestamp(self):
        g = NetworkGraph()
        g.bookmark('content', 'fake_uuid')
        self.assertTrue(isinstance(g.bookmarked_on('fake_uuid'), datetime))

    def test_unbookmark_removes_timestamp(self):
        g = NetworkGraph()
        g.bookmark('content', 'fake_uuid')
        g.unbookmark('content', 'fake_uuid')
        with self.assertRaises(KeyError):
            g.bookmarked_on('fake_uuid')

    def test_get_bookmarks_by_date(self):
        g = NetworkGraph()
        g.bookmark('content', 'fake_uuid_1')
        g.bookmark('content', 'fake_uuid_2')
        bookmarks = g.get_bookmarks_by_date('content')
        self.assertEquals(bookmarks[0].id, 'fake_uuid_1')
        self.assertTrue(bookmarks[1].datetime >= bookmarks[0].datetime)
