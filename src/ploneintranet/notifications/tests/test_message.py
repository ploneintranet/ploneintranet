# -*- coding: utf-8 -*-
from ..message import Message
from datetime import datetime
import unittest2 as unittest


class TestQueue(unittest.TestCase):

    def test_message_creation(self):
        message = Message([], '123', {})
        self.assertEqual([], message.actors)
        self.assertEqual('123', message.predicate)
        self.assertTrue(isinstance(
            message.obj.pop('message_last_modification_date'), datetime))
        self.assertEqual(dict(url='', read=False), message.obj)

    def test_object_is_copied(self):
        obj = {'test': 1}
        message = Message([], '123', obj)
        obj['test'] = 2
        self.assertEqual(1, message.obj['test'])

    def test_message_mark_timestamp(self):
        before_test = datetime.utcnow()
        message = Message([], '123', {})
        self.assertFalse(message.marked_read_at())
        message.mark_as_read()
        read_at = message.marked_read_at()
        self.assertTrue(read_at > before_test)
        message.mark_as_read(before_test)
        # We don't re-set the read times
        self.assertTrue(message.marked_read_at() == read_at)

    def test_message_clone(self):
        message = Message([], '123', {})
        message_cloned = message.clone()
        message.mark_as_read()
        message.actors.append(1)
        message.obj['test'] = 1
        self.assertTrue(message_cloned.is_unread())
        self.assertFalse(len(message_cloned.actors))
        self.assertFalse('test' in message_cloned.obj)

    def test_update_object(self):
        message = Message([], '123', {})
        before = message.obj['message_last_modification_date']
        message.update_object({})
        after = message.obj['message_last_modification_date']
        self.assertTrue(before < after)

    def test_update_actors(self):
        message = Message([1, 2, 3], '123', {})
        message.update_actors(added=[4], removed=[3])
        self.assertEqual([1, 2, 4], message.actors)
