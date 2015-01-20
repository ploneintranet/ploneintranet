# -*- coding: utf-8 -*-
from plone import api
from plone.app.discussion.interfaces import IConversation
from plone.uuid.interfaces import IUUID
from plonesocial.core.integration import PLONESOCIAL
from plonesocial.microblog.statusupdate import StatusUpdate
from plonesocial.network.interfaces import ILikesContainer
from plonesocial.network.testing import IntegrationTestCase
from plonesocial.network.testing import set_browserlayer
from zope.component import createObject
from zope.component import getUtility

import unittest2 as unittest


class TestToggleLikeView(IntegrationTestCase):

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        set_browserlayer(self.request)
        self.util = getUtility(ILikesContainer)
        self.doc1 = api.content.create(
            container=self.portal,
            type='Document',
            id='doc1',
            title='Doc 1'
        )
        self.user_id = api.user.get_current().getId()

    def test_show_like(self):
        view = api.content.get_view('toggle_like', self.portal, self.request)
        self.assertRaises(KeyError, view)
        item_id = api.content.get_uuid(self.doc1)
        view = view.publishTraverse(self.request, item_id)
        output = view()
        self.assertIn('like_button', output)
        self.assertIn(item_id, output)
        self.assertFalse(self.util.is_item_liked_by_user(self.user_id, item_id))

    def test_toggle_like(self):
        self.request.form['like_button'] = 'like'
        view = api.content.get_view('toggle_like', self.portal, self.request)
        item_id = api.content.get_uuid(self.doc1)
        view = view.publishTraverse(self.request, item_id)

        # Toggle like for doc1
        output = view()
        self.assertIn('(1)', output)
        self.assertIn('Unlike', output)
        user_likes = self.util.get_items_for_user(self.user_id)

        self.assertTrue(self.util.is_item_liked_by_user(self.user_id, item_id))
        self.assertEqual(len(user_likes), 1)

        # Toggle like for doc1
        output = view()
        user_likes = self.util.get_items_for_user(self.user_id)
        self.assertEqual(len(user_likes), 0)
        self.assertIn('(0)', output)
        self.assertIn('Like', output)

    def test_multiple_liking(self):
        """Test liking with multiple users and various content
        """
        self.user1 = api.user.create(
            email='john@plone.org',
            username='user1'
        )
        self.user2 = api.user.create(
            email='jane@plone.org',
            username='user2'
        )
        self.all_userids = [
            self.user1.getId(),
            self.user2.getId(),
            'admin',
        ]
        self.doc2 = api.content.create(
            container=self.portal,
            type='Document',
            id='doc2',
            title='Doc 2'
        )

        # 1. All users like doc1
        # 2. user1 and user2 like doc2
        # 3. Check counts and who has liked
        self.util.like(
            user_id=self.all_userids,
            item_id=self.doc1.UID(),
        )
        self.assertEqual(len(self.util._user_uuids_mapping), 3)
        self.assertEqual(len(self.util._uuid_users_mapping), 1)
        self.assertEqual([self.doc1.UID()],
            sorted(list(self.util._uuid_users_mapping)))

        user1_id = self.user1.getId()
        user2_id = self.user2.getId()
        self.util.like(
            user_id=[user1_id, user2_id],
            item_id=self.doc2.UID(),
        )
        results = self.util.get_users_for_item(self.doc2.UID())
        self.assertEqual(len(results), 2)
        self.assertIn(user1_id, results)
        self.assertIn(user2_id, results)


    def test_multiple_liking(self):
        """Test liking with multiple users and various content
        """
        self.user1 = api.user.create(
            email='john@plone.org',
            username='user1'
        )
        self.user2 = api.user.create(
            email='jane@plone.org',
            username='user2'
        )
        self.all_userids = [
            self.user1.getId(),
            self.user2.getId(),
            'admin',
        ]
        self.doc2 = api.content.create(
            container=self.portal,
            type='Document',
            id='doc2',
            title='Doc 2'
        )

        # 1. All users like doc1
        # 2. user1 and user2 like doc2
        # 3. Check counts and who has liked
        self.util.like(
            user_id=self.all_userids,
            item_id=self.doc1.UID(),
        )
        self.assertEqual(len(self.util._user_uuids_mapping), 3)
        self.assertEqual(len(self.util._uuid_users_mapping), 1)
        self.assertEqual([self.doc1.UID()],
            sorted(list(self.util._uuid_users_mapping)))

        user1_id = self.user1.getId()
        user2_id = self.user2.getId()
        self.util.like(
            user_id=[user1_id, user2_id],
            item_id=self.doc2.UID(),
        )
        results = self.util.get_users_for_item(self.doc2.UID())
        self.assertEqual(len(results), 2)
        self.assertIn(user1_id, results)
        self.assertIn(user2_id, results)


    def test_like_discussion_item(self):
        # test discussion-item
        conversation = IConversation(self.doc1)
        comment1 = createObject('plone.Comment')
        conversation.addComment(comment1)
        comment = [i for i in conversation.getComments()][0]
        comment_id = IUUID(comment)

        self.request.form['like_button'] = 'like'
        view = api.content.get_view('toggle_like', self.portal, self.request)
        view = view.publishTraverse(self.request, comment_id)

        # Toggle like for comment
        output = view()
        self.assertIn('(1)', output)
        self.assertIn('Unlike', output)
        user_likes = self.util.get_items_for_user(self.user_id)

        self.assertTrue(self.util.is_item_liked_by_user(self.user_id, comment_id))
        self.assertEqual(len(user_likes), 1)

        # Toggle like for comment
        output = view()
        user_likes = self.util.get_items_for_user(self.user_id)
        self.assertEqual(len(user_likes), 0)
        self.assertIn('(0)', output)
        self.assertIn('Like', output)

    def test_like_status_update(self):
        # test statusupdate
        su = StatusUpdate('Some cool news!')
        container = PLONESOCIAL.microblog
        container.add(su)
        update_id = str(su.id)

        self.request.form['like_button'] = 'like'
        view = api.content.get_view('toggle_like', self.portal, self.request)
        view = view.publishTraverse(self.request, update_id)

        # Toggle like for statusupdate
        output = view()
        self.assertIn('(1)', output)
        self.assertIn('Unlike', output)
        user_likes = self.util.get_items_for_user(self.user_id)

        self.assertTrue(self.util.is_item_liked_by_user(self.user_id, update_id))
        self.assertEqual(len(user_likes), 1)

        # Toggle like for statusupdate
        output = view()
        user_likes = self.util.get_items_for_user(self.user_id)
        self.assertEqual(len(user_likes), 0)
        self.assertIn('(0)', output)
        self.assertIn('Like', output)
