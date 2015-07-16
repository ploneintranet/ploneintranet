# -*- coding: utf-8 -*-

from ..channel import AllChannel
from ..message import Message
from ..testing import PLONEINTRANET_NOTIFICATIONS_INTEGRATION_TESTING
from Products.CMFPlone.utils import getToolByName
from plone import api
from plone.app.testing import TEST_USER_NAME
import unittest


class TestAllChannel(unittest.TestCase):

    layer = PLONEINTRANET_NOTIFICATIONS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        user = api.user.get(username=TEST_USER_NAME)
        tool = getToolByName(self.portal, 'ploneintranet_notifications')

        self.channel = AllChannel(user)
        self.queue = tool.get_user_queue(user)

    def create_test_messages(self):
        for i in range(5):
            obj = {'title': 'Message {}'.format(i + 1)}
            self.queue.append(Message(actors=[], predicate='test', obj=obj))

    def test_queue_empty(self):
        self.assertEqual(0, len(self.channel.get_unread_messages()))
        self.assertEqual(0, len(self.channel.get_unread_messages()))

    def test_queue_not_empty(self):
        self.create_test_messages()
        self.assertEqual(5, len(self.channel.get_unread_messages(
            keep_unread=True)))
        self.assertEqual(5, len(self.channel.get_unread_messages()))
        self.assertEqual(0, len(self.channel.get_unread_messages()))

    def test_read_flag_honoured(self):
        self.assertEqual(0, self.channel.get_unread_count())

        self.create_test_messages()
        self.assertEqual(5, self.channel.get_unread_count())

        self.channel.get_unread_messages(keep_unread=True)
        self.assertEqual(5, self.channel.get_unread_count())

        self.channel.get_unread_messages()
        self.assertEqual(0, self.channel.get_unread_count())

    def test_get_all_messages(self):
        self.create_test_messages()

        self.assertEqual(5, len(self.channel.get_all_messages()))

        self.channel.get_unread_messages()
        self.assertEqual(0, self.channel.get_unread_count())
        self.assertEqual(5, len(self.channel.get_all_messages()))
