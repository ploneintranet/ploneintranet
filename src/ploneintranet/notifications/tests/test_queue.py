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
        user = FakeUser()
        self.assertEqual([], queues.get_user_queue(user.getUserId()))

    def test_getting_filled_data(self):
        queues = Queues()
        user = FakeUser()
        user_queue = queues.get_user_queue(user.getUserId())
        user_queue.append('123')
        self.assertEqual(['123'], queues.get_user_queue(user.getUserId()))

    def test_deleting_data(self):
        queues = Queues()
        user = FakeUser()
        user_queue = queues.get_user_queue(user.getUserId())
        user_queue.append('123')
        queues.del_user_queue(user.getUserId())
        self.assertEqual([], queues.get_user_queue(user.getUserId()))

    def test_delete_all_queues(self):
        queues = Queues()
        user = FakeUser()
        user_queue = queues.get_user_queue(user.getUserId())
        user_queue.append('123')
        queues.clear()
        self.assertEqual([], queues.get_user_queue(user.getUserId()))
