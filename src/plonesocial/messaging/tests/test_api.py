import unittest2 as unittest

from datetime import datetime
now = datetime.now

from plonesocial.messaging.testing import \
    PLONESOCIAL_MESSAGING_INTEGRATION_TESTING


class ApiTestCase(unittest.TestCase):

    layer = PLONESOCIAL_MESSAGING_INTEGRATION_TESTING

    def setUp(self):
        from plonesocial.messaging.messaging import Inboxes
        self.inboxes = Inboxes()

    def _create_inbox(self, username='testuser'):
        return self.inboxes.add_inbox(username)

    def _create_conversation(self, inbox_user='testuser',
                             other_user='otheruser',
                             created=None):
        from plonesocial.messaging.messaging import Conversation
        if created is None:
            created = now()
        inbox = self._create_inbox(username=inbox_user)
        return inbox.add_conversation(Conversation(other_user, created))


class TestInboxs(ApiTestCase):

    def test_inboxes_add_inbox(self):
        from plonesocial.messaging.messaging import Inbox
        self.assertEqual(list(self.inboxes.keys()), [])
        self.inboxes.add_inbox('testuser')
        self.assertEqual(list(self.inboxes.keys()), ['testuser'])
        self.assertTrue(type(self.inboxes['testuser']) is Inbox)

    def test_inboxes_get_inbox_creates_inbox(self):
        self.assertEqual(list(self.inboxes.keys()), [])
        new_inbox = self.inboxes.get_inbox('testuser')
        self.assertEqual(list(self.inboxes.keys()), ['testuser'])
        self.assertTrue(new_inbox is self.inboxes['testuser'])

    def test_inboxes_get_existing_inbox(self):
        existing_inbox = self._create_inbox('testuser')
        self.assertTrue(self.inboxes.get_inbox('testuser') is existing_inbox)


class TestInbox(ApiTestCase):

    def test_inbox_provides_iinbox(self):
        from plonesocial.messaging.interfaces import IInbox
        new_inbox = self.inboxes.get_inbox('testuser')
        self.assertTrue(IInbox.providedBy(new_inbox))

    def test_inbox_get_empty_conversations(self):
        inbox = self._create_inbox()
        self.assertEqual(list(inbox.get_conversations()), [])

    def test_inbox_get_conversations(self):
        from plonesocial.messaging.messaging import Conversation
        inbox = self._create_inbox()
        inbox.add_conversation(Conversation('otheruser', now()))
        inbox.add_conversation(Conversation('thirduser', now()))
        conversations = inbox.get_conversations()
        self.assertEqual(len(conversations), 2)
        self.assertEqual(type(conversations[0]), Conversation)
        self.assertEqual(type(conversations[1]), Conversation)
        self.assertTrue(conversations[0] != conversations[1])

    def test_inbox_add_conversation(self):
        from plonesocial.messaging.messaging import Conversation
        inbox = self._create_inbox()
        conversation = Conversation('otheruser', now())
        inbox.add_conversation(conversation)
        conversation = inbox.get_conversation('otheruser')
        self.assertEqual(type(conversation), Conversation)

    def test_inbox_delete_conversation(self):
        from plonesocial.messaging.messaging import Conversation
        inbox = self._create_inbox()
        inbox.add_conversation(Conversation('otheruser', now()))
        conversations = inbox.get_conversations()
        self.assertEqual(len(conversations), 1)
        inbox.delete_conversation('otheruser')
        conversations = inbox.get_conversations()
        self.assertEqual(len(conversations), 0)

    def test_inbox_user_initially_isnt_blocked(self):
        inbox = self._create_inbox()
        self.assertEqual(inbox.is_blocked('dontlike'), False)

    def test_inbox_block_user(self):
        return  # FIXME: not implemented yet
        inbox = self._create_inbox()
        inbox.block_user('dontlike')
        self.assertEqual(inbox.is_blocked('dontlike'), True)

    def test_inbox_initial_unread_messages_count(self):
        inbox = self._create_inbox()
        self.assertEqual(inbox.unread_messages_count, 0)


class TestConversation(ApiTestCase):

    def test_conversation_initially_has_no_message(self):
        conversation = self._create_conversation()
        self.assertEqual(list(conversation.get_messages()), [])

    def test_conversation_initial_message_count_is_zero(self):
        conversation = self._create_conversation()
        self.assertEqual(conversation.unread_messages_count, 0)

    def test_conversation_add_message(self):
        from plonesocial.messaging.messaging import Message
        conversation = self._create_conversation('inbox_user', 'other_user')
        message = Message('inbox_user', 'other_user', 'test', now())
        conversation.add_message(message)
        messages = conversation.get_messages()
        self.assertEqual(list(messages), [message])

    def test_conersation_add_message_unread_count(self):
        from plonesocial.messaging.messaging import Message
        conversation = self._create_conversation('inbox_user', 'other_user')
        self.assertEqual(conversation.unread_messages_count, 0)

        message = Message('inbox_user', 'other_user', 'test', now())
        conversation.add_message(message)
        self.assertEqual(list(conversation.get_messages())[0].read, False)
        self.assertEqual(conversation.unread_messages_count, 1)

    def test_conversation_mark_read(self):
        from plonesocial.messaging.messaging import Message
        conversation = self._create_conversation('inbox_user', 'other_user')
        message = Message('inbox_user', 'other_user', 'test', now())
        conversation.add_message(message)
        self.assertEqual(message.read, False)
        conversation.mark_read()
        self.assertEqual(conversation.unread_messages_count, 0)
        self.assertEqual(message.read, True)
