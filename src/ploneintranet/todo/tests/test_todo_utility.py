from datetime import datetime, timedelta
from faker import Factory
from plone import api
from zope.component import getUtility
from zope.interface.verify import verifyClass

from ..interfaces import ITodoUtility, TODO, MUST_READ
from ..content.content_action import ContentAction
from ..todo_utility import TodoUtility
from ..testing import IntegrationTestCase


class TestTodoUtility(IntegrationTestCase):

    def setUp(self):
        self.faker = Factory.create()
        self.portal = self.layer['portal']
        self.util = getUtility(ITodoUtility)
        self.user1 = api.user.create(
            email=self.faker.company_email(),
            username='user1'
        )
        self.user2 = api.user.create(
            email=self.faker.company_email(),
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

    def add_test_actions(self):
        # 1. Add a todo for all users (4 users) on doc1
        # 2. Add a read for user1 and 2 on doc2
        # 3. Add a create for admin on doc2 (completed)
        # 4. Add a create for user1 on doc1 (completed)
        user1_id = self.user1.getId()
        user2_id = self.user2.getId()
        doc1_uid = self.doc1.UID()
        doc2_uid = self.doc2.UID()
        self.util.add_action(
            doc1_uid,
            TODO
        )
        self.util.add_action(
            doc2_uid,
            MUST_READ,
            [user1_id, user2_id]
        )
        self.util.add_action(
            doc2_uid,
            'create',
            'admin'
        )
        self.util.complete_action(
            doc2_uid,
            'create',
            'admin'
        )
        self.util.add_action(
            doc1_uid,
            'create',
            user1_id
        )
        self.util.complete_action(
            doc1_uid,
            'create',
            user1_id
        )

    def add_actions_for_sort_test(self):
        user1_id = self.user1.getId()
        storage = self.util._get_storage()
        created = self.faker.date_time_between(
            start_date='-1m',
            end_date='now'
        )
        user_actions = []
        for _ in range(10):
            action = ContentAction(
                user1_id,
                self.faker.md5(),
                TODO,
                created=created
            )
            created += timedelta(minutes=10)
            user_actions.append(action)
        storage[user1_id] = user_actions

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
            TODO,
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
        self.assertEqual(action.verb, TODO)
        self.assertLess(action.created, datetime.now())
        self.assertIsNone(action.completed)
        self.assertIsNone(action.modified)

    def test_add_action_for_some_users(self):
        user1_id = self.user1.getId()
        user2_id = self.user2.getId()
        doc1_uid = self.doc1.UID()
        self.util.add_action(
            doc1_uid,
            TODO,
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
            TODO
        )
        storage = self.util._get_storage()
        self.assertEqual(
            len(storage.keys()),
            len(self.all_userids)
        )

    def test_query_no_params(self):
        self.add_test_actions()
        results = self.util.query()
        self.assertEqual(len(results), 6)

    def test_query_userids(self):
        self.add_test_actions()
        user1_id = self.user1.getId()
        user2_id = self.user2.getId()
        results = self.util.query(
            userids=user1_id
        )
        self.assertEqual(len(results), 2)
        results = self.util.query(
            userids=[user1_id, user2_id]
        )
        self.assertEqual(len(results), 4)

    def test_query_verbs(self):
        self.add_test_actions()
        results = self.util.query(
            verbs=TODO
        )
        self.assertEqual(len(results), 4)
        results = self.util.query(
            verbs=[TODO, MUST_READ]
        )
        self.assertEqual(len(results), 6)

    def test_query_content_uids(self):
        self.add_test_actions()
        doc1_uid = self.doc1.UID()
        doc2_uid = self.doc2.UID()
        results = self.util.query(
            content_uids=doc1_uid
        )
        self.assertEqual(len(results), 4)
        results = self.util.query(
            content_uids=[doc1_uid, doc2_uid]
        )
        self.assertEqual(len(results), 6)

    def test_query_sort(self):
        self.add_actions_for_sort_test()
        self.maxDiff = None
        results = [
            x.created for x in
            self.util.query(sort_on='created')
        ]
        old_results_reversed = sorted(results, reverse=True)
        results = [
            x.created for x in
            self.util.query(
                sort_on='created',
                sort_order='reverse'
            )
        ]
        self.assertEqual(results, old_results_reversed)

    def test_query_ignore_completed(self):
        self.add_test_actions()
        results = self.util.query(ignore_completed=False)
        self.assertEqual(len(results), 8)

    def test_remove_action(self):
        user1_id = self.user1.getId()
        doc1_uid = self.doc1.UID()
        self.util.add_action(
            doc1_uid,
            TODO,
            user1_id
        )
        results = self.util.query(
            user1_id
        )
        self.assertEqual(len(results), 1)
        self.util.remove_action(
            doc1_uid,
            TODO,
            user1_id
        )
        results = self.util.query(
            user1_id
        )
        self.assertEqual(len(results), 0)

    def test_add_remove_complete_action(self):
        """
        Ensure that complete_action can be performed after adding and removing
        all actions.
        """
        doc1_uid = self.doc1.UID()
        self.util.add_action(doc1_uid, TODO)
        self.util.remove_action(doc1_uid, TODO)
        self.util.complete_action(doc1_uid, TODO)
