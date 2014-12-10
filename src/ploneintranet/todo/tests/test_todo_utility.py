from datetime import datetime
from faker import Factory
from plone import api
from zope.component import getUtility
from zope.interface.verify import verifyClass

from ..interfaces import ITodoUtility
from ..content.content_action import ContentAction
from ..todo_utility import TodoUtility
from ..testing import IntegrationTestCase


class TestTodoUtility(IntegrationTestCase):

    def setUp(self):
        faker = Factory.create()
        self.portal = self.layer['portal']
        self.util = getUtility(ITodoUtility)
        self.user1 = api.user.create(
            email=faker.company_email(),
            username='user1'
        )
        self.user2 = api.user.create(
            email=faker.company_email(),
            username='user2'
        )
        self.all_userids = {
            self.user1.getId(),
            self.user2.getId(),
            'admin',
            'test_user_1_',
        }
        self.doc1 = api.content.create(
            container=self.portal,
            type='Document',
            id='doc1',
            title='Doc 1'
        )
        self.doc2 = api.content.create(
            container=self.portal,
            type='Document',
            id='doc2',
            title='Doc 2'
        )

    def test_implements_interface(self):
        self.assertTrue(verifyClass(ITodoUtility, TodoUtility))

    def test__get_storage(self):
        storage = self.util._get_storage()
        key = 'foo'
        value = 'bar'
        storage[key] = value
        self.assertEqual(
            self.util._get_storage().get(key),
            value
        )

    def test__all_users(self):
        self.assertEqual(
            set(self.util._all_users()),
            self.all_userids,
        )

    def test__user_in_storage(self):
        user1_id = self.user1.getId()
        storage = self.util._get_storage()
        storage[user1_id] = 'foo'
        self.assertTrue(self.util._user_in_storage(user1_id))

    def test_add_action_for_one_user(self):
        user1_id = self.user1.getId()
        doc1_uid = self.doc1.UID()
        self.util.add_action(
            doc1_uid,
            'todo',
            userids=user1_id
        )
        storage = self.util._get_storage()
        self.assertEqual(len(storage.keys()), 1)
        actions = storage[user1_id]
        self.assertEqual(len(actions), 1)
        action = actions[0]
        self.assertIsInstance(action, ContentAction)
        self.assertEqual(action.userid, user1_id)
        self.assertEqual(action.content_uid, doc1_uid)
        self.assertEqual(action.verb, 'todo')
        self.assertLess(action.created, datetime.now())
        self.assertIsNone(action.completed)
        self.assertIsNone(action.modified)

    def test_add_action_for_some_users(self):
        user1_id = self.user1.getId()
        user2_id = self.user2.getId()
        doc1_uid = self.doc1.UID()
        self.util.add_action(
            doc1_uid,
            'todo',
            userids=[user1_id, user2_id]
        )
        storage = self.util._get_storage()
        self.assertEqual(len(storage.keys()), 2)
        self.assertIn(user1_id, storage.keys())
        self.assertIn(user2_id, storage.keys())

    def test_add_action_for_all_users(self):
        doc1_uid = self.doc1.UID()
        self.util.add_action(
            doc1_uid,
            'todo'
        )
        storage = self.util._get_storage()
        self.assertEqual(
            len(storage.keys()),
            len(self.all_userids)
        )

    def add_test_actions(self):
        user1_id = self.user1.getId()
        user2_id = self.user2.getId()
        doc1_uid = self.doc1.UID()
        doc2_uid = self.doc2.UID()

    def test_query_no_params(self):
        self.fail()