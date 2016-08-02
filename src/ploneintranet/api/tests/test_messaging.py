# -*- coding: utf-8 -*-
from datetime import datetime
from ploneintranet.api.testing import IntegrationTestCase
from ploneintranet import api as pi_api
from ploneintranet.api import messaging
from ploneintranet.messaging import interfaces


class TestMessagingApi(IntegrationTestCase):

    def setUp(self):
        IntegrationTestCase.setUp(self)
        self.login_as_portal_owner()
        pi_api.userprofile.create(
            username='johndoe',
            email='johndoe@doe.com',
            approve=True,
        )
        pi_api.userprofile.create(
            username='maryjane',
            email='mary@jane.com',
            approve=True,
        )

    def test_send_explicit(self):
        self.assertNotIn('maryjane', messaging.get_inboxes())
        self.assertNotIn('johndoe', messaging.get_inboxes())
        messaging.send_message(
            'maryjane', 'Hi Mary', 'johndoe', datetime(2014, 2, 2))
        self.assertIn('maryjane', messaging.get_inboxes())
        self.assertIn('johndoe', messaging.get_inboxes())

    def test_send_defaults(self):
        self.login('johndoe')
        self.assertNotIn('johndoe', messaging.get_inboxes())
        messaging.send_message('maryjane', 'Hi Mary')
        self.assertIn('johndoe', messaging.get_inboxes())

    def test_get_inboxes(self):
        inboxes = messaging.get_inboxes()
        self.assertTrue(interfaces.IInboxes.providedBy(inboxes))

    def test_get_inbox(self):
        self.login('johndoe')
        messaging.send_message('maryjane', 'Hi Mary')
        inbox = messaging.get_inbox()
        self.assertTrue(interfaces.IInbox.providedBy(inbox))

    def test_get_conversation(self):
        self.login('johndoe')
        messaging.send_message('maryjane', 'Hi Mary')
        conversation = messaging.get_conversation('maryjane')
        self.assertTrue(interfaces.IConversation.providedBy(conversation))

    def test_get_messages(self):
        self.login('johndoe')
        messaging.send_message('maryjane', 'Hi Mary')
        messages = [x for x in messaging.get_messages('maryjane')]
        self.assertEquals(1, len(messages))
        message = messages[0]
        self.assertTrue(interfaces.IMessage.providedBy(message))
        self.assertEquals('johndoe', message.sender)
        self.assertEquals('maryjane', message.recipient)
