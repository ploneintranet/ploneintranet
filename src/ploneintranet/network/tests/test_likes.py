# -*- coding: utf-8 -*-
import time
import unittest2 as unittest
from ploneintranet.network.graph import NetworkGraph


class TestLikeContent(unittest.TestCase):

    def setUp(self):
        # self.portal = self.layer['portal']
        self.userid = 'testperson@test.org'
        self.object_uuid = '827e65bd826a89790eba679e0c9ff864'
        self.container = NetworkGraph()

    def _like_content(self):
        self.container.like("content", self.object_uuid, self.userid, )

    def test_like_content(self):
        self._like_content()

        liked_items = self.container.get_likes("content", self.userid)
        self.assertEqual(sorted(list(liked_items)), [self.object_uuid])

        liking_users = self.container.get_likers("content", self.object_uuid)
        self.assertEqual(sorted(list(liking_users)), [self.userid])

    def test_like_content_utf8(self):
        userid = u'M♥rÿ@test.org'
        self.container.like("content", self.object_uuid, userid, )
        liked_items = self.container.get_likes("content", userid)
        self.assertEqual(sorted(list(liked_items)), [self.object_uuid])
        liking_users = self.container.get_likers("content", self.object_uuid)
        self.assertEqual(sorted(list(liking_users)), [userid])

    def test_utf8_args(self):
        """BTree keys MUST be of type unicode. Check that the implementation
        enforces this."""
        g = NetworkGraph()
        self.assertRaises(AttributeError, g.like, 'content', 1, '2')
        self.assertRaises(AttributeError, g.like, 'content', '1', 2)
        self.assertRaises(AttributeError, g.unlike, 'content', 1, '2')
        self.assertRaises(AttributeError, g.unlike, 'content', '1', 2)
        self.assertRaises(AttributeError, g.get_likes, 'content', 1)
        self.assertRaises(AttributeError, g.get_likers, 'content', 1)
        self.assertRaises(AttributeError, g.is_liked, 'content', 1, 2)

    def test_content_liked_by_two_users(self):
        self._like_content()
        self.container.like("content", self.object_uuid, 'cyclon@test.org', )

        liked_items = self.container.get_likes("content", self.userid)
        self.assertEqual(sorted(list(liked_items)), [self.object_uuid])
        liked_items = self.container.get_likes("content", 'cyclon@test.org')
        self.assertEqual(sorted(list(liked_items)), [self.object_uuid])

        liking_users = self.container.get_likers("content", self.object_uuid)
        self.assertEqual(
            sorted(list(liking_users)),
            ['cyclon@test.org', self.userid])

    def test_unlike_content(self):
        self._like_content()
        self.container.unlike("content", self.object_uuid, self.userid)

        liked_items = self.container.get_likes("content", self.userid)
        self.assertEqual(sorted(list(liked_items)), [])

        liking_users = self.container.get_likers("content", self.object_uuid)
        self.assertEqual(sorted(list(liking_users)), [])

    def test_get_content_likes(self):
        self._like_content()
        self.assertEqual(
            sorted(list(self.container.get_likes("content", self.userid))),
            [self.object_uuid])

    def test_get_content_likes_empty(self):
        self.assertEqual(self.container.get_likes("content", self.userid), [])

    def test_is_content_liked(self):
        self.assertFalse(
            self.container.is_liked("content", self.object_uuid, self.userid))

        self._like_content()

        self.assertTrue(
            self.container.is_liked("content", self.object_uuid, self.userid))

    def test_get_content_likers(self):
        self._like_content()
        self.assertIn(
            self.userid,
            self.container.get_likers("content", self.object_uuid)
        )

    def test_get_content_likers_empty(self):
        self.assertEqual(
            self.container.get_likers("content", self.object_uuid), []
        )


class TestLikeUpdate(unittest.TestCase):

    def setUp(self):
        # self.portal = self.layer['portal']
        self.userid = 'testperson@test.org'
        self.statusid = str(long(time.time() * 1e6))
        self.container = NetworkGraph()

    def _like_update(self):
        self.container.like("update", self.statusid, self.userid)

    def test_like_update(self):
        self._like_update()

        liked_items = self.container.get_likes("update", self.userid)
        self.assertEqual(sorted(list(liked_items)), [self.statusid])

        liking_users = self.container.get_likers("update", self.statusid)
        self.assertEqual(sorted(list(liking_users)), [self.userid])

    def test_update_liked_by_two_users(self):
        self._like_update()
        self.container.like("update", self.statusid, 'cyclon@test.org')

        liked_items = self.container.get_likes("update", self.userid)
        self.assertEqual(sorted(list(liked_items)), [self.statusid])
        liked_items = self.container.get_likes("update", 'cyclon@test.org')
        self.assertEqual(sorted(list(liked_items)), [self.statusid])

        liking_users = self.container.get_likers("update", self.statusid)
        self.assertEqual(
            sorted(list(liking_users)),
            ['cyclon@test.org', self.userid])

    def test_unlike_update(self):
        self._like_update()

        self.container.unlike("update", self.statusid, self.userid)

        liked_items = self.container.get_likes("update", self.userid)
        self.assertEqual(sorted(list(liked_items)), [])

        liking_users = self.container.get_likers("update", self.statusid)
        self.assertEqual(sorted(list(liking_users)), [])

    def test_get_update_likes(self):
        self._like_update()
        self.assertEqual(
            sorted(list(self.container.get_likes("update", self.userid))),
            [self.statusid])

    def test_get_update_likes_empty(self):
        self.assertEqual(self.container.get_likes("update", self.userid), [])

    def test_is_update_liked(self):
        self.assertFalse(
            self.container.is_liked("update", self.statusid, self.userid))

        self._like_update()

        self.assertTrue(
            self.container.is_liked("update", self.statusid, self.userid))

    def test_get_update_likers(self):
        self._like_update()
        self.assertIn(
            self.userid,
            self.container.get_likers("update", self.statusid)
        )

    def test_get_update_likers_empty(self):
        self.assertEqual(
            self.container.get_likers("update", self.statusid), []
        )


class TestLikeMixed(unittest.TestCase):

    def setUp(self):
        self.userid = 'testperson@test.org'
        self.object_uuid = '827e65bd826a89790eba679e0c9ff864'
        self.statusid = str(long(time.time() * 1e6))
        self.container = NetworkGraph()

    def assertIterEqual(self, iterA, iterB):
        return self.assertEqual([x for x in iterA],
                                [x for x in iterB])

    def test_like_mixed(self):
        self.assertIterEqual(self.container.get_likes(
            "content", self.userid), [])
        self.assertIterEqual(self.container.get_likes(
            "update", self.userid), [])

        self.container.like("content", self.object_uuid, self.userid)
        self.container.like("update", self.statusid, self.userid)
        self.assertIterEqual(self.container.get_likes(
            "content", self.userid), [self.object_uuid])
        self.assertIterEqual(self.container.get_likes(
            "update", self.userid), [self.statusid])

        self.container.unlike("content", self.object_uuid, self.userid)
        self.container.unlike("update", self.statusid, self.userid)
        self.assertIterEqual(self.container.get_likes(
            "content", self.userid), [])
        self.assertIterEqual(self.container.get_likes(
            "update", self.userid), [])
