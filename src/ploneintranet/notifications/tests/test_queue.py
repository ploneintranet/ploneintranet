# -*- coding: utf-8 -*-

from ploneintranet.notifications.queue import Queues
import unittest2 as unittest


class TestQueue(unittest.TestCase):

    def test_getting_empty_data(self):
        queues = Queues()
        self.assertEqual([], queues.get_user_queue('newuser'))

    def test_getting_filled_data(self):
        queues = Queues()
        user_queue = queues.get_user_queue('testuser')
        user_queue.append('123')
        self.assertEqual(['123'], queues.get_user_queue('testuser'))

    def test_deleting_data(self):
        queues = Queues()
        user_queue = queues.get_user_queue('testuser')
        user_queue.append('123')
        queues.del_user_queue('testuser')
        self.assertEqual([], queues.get_user_queue('testuser'))
