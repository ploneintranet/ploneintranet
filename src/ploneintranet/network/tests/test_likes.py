# -*- coding: utf-8 -*-
import unittest2 as unittest
from plone import api
from ploneintranet.network.interfaces import ILikesContainer
from ploneintranet.network.interfaces import ILikesTool
from ploneintranet.network.likes import LikesContainer
from ploneintranet.network.testing import IntegrationTestCase
from zope.component import queryUtility


class TestLikesTool(IntegrationTestCase):

    def setUp(self):
        self.portal = self.layer['portal']

    def test_likes_tool_available(self):
        tool = queryUtility(ILikesTool)
        self.assertTrue(ILikesContainer.providedBy(tool))

    def test_likes_tool_uninstalled(self):
        qi = self.portal['portal_quickinstaller']
        with api.env.adopt_roles(['Manager']):
            qi.uninstallProducts(products=['ploneintranet.network'])
        self.assertNotIn('ploneintranet_likes', self.portal)
        tool = queryUtility(ILikesTool, None)
        self.assertIsNone(tool)


class TestLikes(unittest.TestCase):

    def setUp(self):
        # self.portal = self.layer['portal']
        self.userid = 'testperson@test.org'
        self.object_uuid = '827e65bd826a89790eba679e0c9ff864'
        self.container = LikesContainer()

    def _like_content(self):
        self.container.like_content(
            self.userid, self.object_uuid)

    def test_like_content(self):
        self._like_content()

        liked_items = self.container._user_content_mapping[self.userid]
        self.assertEqual(sorted(list(liked_items)), [self.object_uuid])

        liking_users = self.container._content_user_mapping[self.object_uuid]
        self.assertEqual(sorted(list(liking_users)), [self.userid])

    def test_content_liked_by_two_users(self):
        self._like_content()
        self.container.like_content(
            'cyclon@test.org', self.object_uuid)

        liked_items = self.container._user_content_mapping[self.userid]
        self.assertEqual(sorted(list(liked_items)), [self.object_uuid])
        liked_items = self.container._user_content_mapping['cyclon@test.org']
        self.assertEqual(sorted(list(liked_items)), [self.object_uuid])

        liking_users = self.container._content_user_mapping[self.object_uuid]
        self.assertEqual(
            sorted(list(liking_users)),
            ['cyclon@test.org', self.userid])

    def test_unlike_content(self):
        self._like_content()

        self.container.unlike_content(self.userid, self.object_uuid)

        liked_items = self.container._user_content_mapping[self.userid]
        self.assertEqual(sorted(list(liked_items)), [])

        liking_users = self.container._content_user_mapping[self.object_uuid]
        self.assertEqual(sorted(list(liking_users)), [])

    def test_get_content_likes(self):
        self._like_content()
        self.assertEqual(
            sorted(list(self.container.get_content_likes(self.userid))),
            [self.object_uuid])

    def test_get_content_likes_empty(self):
        self.assertEqual(self.container.get_content_likes(self.userid), [])

    def test_is_content_liked_by_user(self):
        self.assertFalse(
            self.container.is_content_liked_by_user(
                self.userid,
                self.object_uuid))

        self._like_content()

        self.assertTrue(
            self.container.is_content_liked_by_user(
                self.userid,
                self.object_uuid))

    def test_get_content_likers(self):
        self._like_content()
        self.assertIn(
            self.userid,
            self.container.get_content_likers(self.object_uuid)
        )

    def test_get_content_likers_empty(self):
        self.assertEqual(
            self.container.get_content_likers(self.object_uuid), []
        )
