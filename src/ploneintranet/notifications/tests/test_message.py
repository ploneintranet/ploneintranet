# -*- coding: utf-8 -*-

from datetime import datetime
from ploneintranet.notifications.message import Message
from ploneintranet.notifications.message import create_message
import unittest2 as unittest


class TestQueue(unittest.TestCase):

    def test_message_creation(self):
        message = create_message([], '123', {})
        self.assertTrue(isinstance(message, Message))
        self.assertEqual([], message.actors)
        self.assertEqual('123', message.predicate)
        self.assertTrue(isinstance(
            message.obj.pop('message_last_modification_date'), datetime))
        self.assertEqual(dict(url='', read=False), message.obj)

    def test_message_actors_are_persistent(self):
        message = create_message([], '123', {})
        self.assertNotEqual(type(message.actors), list)

    def test_object_is_copied(self):
        obj = {'test': 1}
        message = create_message([], '123', obj)
        obj['test'] = 2
        self.assertEqual(1, message.obj['test'])
