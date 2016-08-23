# -*- coding: utf-8 -*-

from plone.app.testing import TEST_USER_NAME
from ploneintranet.notifications.queue import Queues
import unittest2 as unittest


class FakeUser(object):
    def getUserId(self):
        return TEST_USER_NAME


class TestQueue(unittest.TestCase):

    def test_getting_empty_data(self):
        queues = Queues()
        self.assertTupleEqual(
            queues.get_user_queue('a-user'),
            (),
        )

    def test_getting_filled_data(self):
        queues = Queues()
        queues.append_to_user_queue('a-user', '123')
        self.assertTupleEqual(
            queues.get_user_queue('a-user'),
            ('123',),
        )

    def test_getting_data_with_limit(self):
        queues = Queues()
        for idx in range(10):
            queues.append_to_user_queue('a-user', idx)
        self.assertTupleEqual(
            queues.get_user_queue('a-user', limit=5),
            (0, 1, 2, 3, 4),
        )

    def test_deleting_data(self):
        queues = Queues()
        queues.append_to_user_queue('a-user', '123')
        queues.del_user_queue('a-user')
        self.assertTupleEqual(
            queues.get_user_queue('a-user'),
            (),
        )

    def test_delete_all_queues(self):
        queues = Queues()
        queues.append_to_user_queue('a-user', '123')
        queues.clear()
        self.assertTupleEqual(
            queues.get_user_queue('a-user'),
            (),
        )
