# -*- coding: utf-8 -*-

from ..channel import AllChannel
from ..message import Message
from ..testing import FunctionalTestCase
from Products.CMFPlone.utils import getToolByName
from plone import api
from plone.app.testing import TEST_USER_NAME


class TestAllChannel(FunctionalTestCase):

    def setUp(self):
        self.portal = self.layer['portal']
        self.user = api.user.get(username=TEST_USER_NAME)
        self.tool = getToolByName(self.portal, 'ploneintranet_notifications')
        self.channel = AllChannel(self.user.getId())

    def create_test_messages(self):
        for i in range(5):
            obj = {'title': 'Message {}'.format(i + 1)}
            self.tool.append_to_user_queue(
                self.user.getId(),
                Message(actors=[], predicate='test', obj=obj)
            )

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
