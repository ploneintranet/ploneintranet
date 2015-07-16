# -*- coding: utf-8 -*-
from ..message import Message
from Products.CMFPlone.utils import getToolByName
from plone import api
from plone.app.testing import TEST_USER_NAME
from ploneintranet.notifications.interfaces import IMessageClassHandler
from ploneintranet.notifications.testing import \
    PLONEINTRANET_NOTIFICATIONS_INTEGRATION_TESTING
from zope.component import getAdapter
import unittest


class TestGenericMessageClassHandler(unittest.TestCase):

    layer = PLONEINTRANET_NOTIFICATIONS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        user1 = api.user.get(username=TEST_USER_NAME)
        user2 = api.user.create(email='a@example.com',
                                username='user').getUser()
        tool = getToolByName(self.portal, 'ploneintranet_notifications')

        self.msg_class_handler = getAdapter(
            self.portal, IMessageClassHandler, name='GLOBAL_NOTICE'
        )
        self.queue1 = tool.get_user_queue(user1.getUserId())
        self.queue2 = tool.get_user_queue(user2.getUserId())

    def test_adding(self):
        message = Message(actors=[], predicate='GLOBAL_NOTICE', obj={})
        self.msg_class_handler.add(message)
        self.assertEqual(1, len(self.queue1))

    def test_adding_creates_unique_messages(self):
        message = Message(actors=[], predicate='GLOBAL_NOTICE', obj={})
        self.msg_class_handler.add(message)
        self.assertEqual(1, len(self.queue1))
        self.assertEqual(1, len(self.queue2))
        self.assertNotEqual(self.queue1[0], self.queue2[0])

    def test_cleanup(self):
        message = Message(actors=[], predicate='GLOBAL_NOTICE', obj={})
        self.msg_class_handler.add(message)
        self.queue1[0].mark_as_read()
        self.assertEqual(1, len(self.queue1))
        self.assertEqual(1, len(self.queue2))

        self.msg_class_handler.cleanup()
        self.assertEqual(1, len(self.queue2))
        self.assertEqual(0, len(self.queue1))
