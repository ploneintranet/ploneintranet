# -*- coding: utf-8 -*-
from plone import api
from plonesocial.network.interfaces import ILikesContainer
from plonesocial.network.interfaces import ILikesTool
from plonesocial.network.likes import LikesContainer
from plonesocial.network.testing import IntegrationTestCase
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
            qi.uninstallProducts(products=['plonesocial.network'])
        self.assertNotIn('plonesocial_likes', self.portal)
        tool = queryUtility(ILikesTool, None)
        self.assertIsNone(tool)


class TestLikes(IntegrationTestCase):

    def setUp(self):
        # self.portal = self.layer['portal']
        self.userid = 'testperson@test.org'
        self.object_uuid = '827e65bd826a89790eba679e0c9ff864'
        self.container = LikesContainer()

    def _add(self):
        self.container.add(
            self.userid, self.object_uuid)

    def test_add(self):
        self._add()

        liked_items = self.container._user_uuids_mapping[self.userid]
        self.assertEqual(sorted(list(liked_items)), [self.object_uuid])

        liking_users = self.container._uuid_users_mapping[self.object_uuid]
        self.assertEqual(sorted(list(liking_users)), [self.userid])

    def test_liked_by_two_users(self):
        self._add()
        self.container.add(
            'cyclon@test.org', self.object_uuid)

        liked_items = self.container._user_uuids_mapping[self.userid]
        self.assertEqual(sorted(list(liked_items)), [self.object_uuid])
        liked_items = self.container._user_uuids_mapping['cyclon@test.org']
        self.assertEqual(sorted(list(liked_items)), [self.object_uuid])

        liking_users = self.container._uuid_users_mapping[self.object_uuid]
        self.assertEqual(
            sorted(list(liking_users)),
            ['cyclon@test.org', self.userid])

    def test_remove(self):
        self._add()

        self.container.remove(self.userid, self.object_uuid)

        liked_items = self.container._user_uuids_mapping[self.userid]
        self.assertEqual(sorted(list(liked_items)), [])

        liking_users = self.container._uuid_users_mapping[self.object_uuid]
        self.assertEqual(sorted(list(liking_users)), [])

    def test_get(self):
        self._add()
        self.assertEqual(
            sorted(list(self.container.get(self.userid))), [self.object_uuid])

    def test_get_empty(self):
        self.assertEqual(self.container.get(self.userid), [])

    def test_lookup(self):
        self._add()
        self.assertEqual(
            sorted(list(self.container.lookup(self.object_uuid))),
            [self.userid]
        )

    def test_lookup_empty(self):
        self.assertEqual(
            self.container.lookup(self.object_uuid), [])

    def test_is_item_liked_by_user(self):
        self.assertFalse(
            self.container.is_item_liked_by_user(
                self.userid,
                self.object_uuid))

        self._add()

        self.assertTrue(
            self.container.is_item_liked_by_user(
                self.userid,
                self.object_uuid))

    def test_get_items_for_user(self):
        self._add()
        self.assertIn(
            self.object_uuid,
            self.container.get_items_for_user(self.userid)
        )

    def test_get_users_for_item(self):
        self._add()
        self.assertIn(
            self.userid,
            self.container.get_users_for_item(self.object_uuid)
        )
