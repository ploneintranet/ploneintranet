from datetime import datetime
import time

from BTrees.LOBTree import LOBTree
from BTrees.OOBTree import OOBTree
from Persistence import Persistent
from zope.interface import implementer

from plonesocial.messaging.interfaces import IConversation, IInbox, IInboxes
from plonesocial.messaging.interfaces import IMessage, IMessagingLocator


@implementer(IMessage)
class Message(Persistent):

    __parent__ = None

    sender = None
    recipient = None
    text = None
    created = None
    deleted = None
    uuid = None
    read = False

    def __init__(self, sender, recipient, text, created):
        if sender == recipient:
            raise ValueError('Sender and recipient are identical'
                             '(%s, %s)' % (sender, recipient))  # FIXME: test
        if not text.strip():
            raise ValueError('Message has no text')  # FIXME: test

        self.sender = sender
        self.recipient = recipient
        self.text = text
        self.created = created


@implementer(IConversation)
class Conversation(Persistent):

    __parent__ = None

    username = None
    last_updated = None
    new_messages_count = 0

    def __init__(self, username, created):
        self.username = username
        self.last_updated
        self._messages = LOBTree()

    def to_long(self, dt):
        """Turns a `datetime` object into a long"""
        return long(time.mktime(dt.timetuple()) * 1000000 + dt.microsecond)

    def add_message(self, message):
        # FIXME: test collision / good key?
        timestamp = self.to_long(message.created)
        while timestamp in self._messages:
            timestamp = timestamp + 1
        message.uid = timestamp
        message.__parent__ = self
        self._messages[timestamp] = message
        if not message.read:
            self.new_messages_count = self.new_messages_count + 1
        return timestamp

    def get_messages(self):
        return self._messages.values()

    def mark_read(self):
        self.new_messages_count = 0
        for message in self._messages.values():
            message.read = True


@implementer(IInbox)
class Inbox(Persistent):

    __parent__ = None

    new_messages_count = 0
    username = None

    def __init__(self, username):
        self.username = username
        self._conversations = OOBTree()

    def add_conversation(self, conversation):
        if conversation.username == self.username:
            raise ValueError("You can't speak to yourself")  # FIXME: test
        if conversation.username in self._conversations:
            raise ValueError(
                "Conversation for user '%s' already exists" %
                conversation.username)
        self._conversations[conversation.username] = conversation
        conversation.__parent__ = self
        return conversation

    def get_conversation(self, username):
        # FIXME: autocreate?
        if username not in self._conversations:
            conversation = Conversation(username, datetime.now())
            self.add_conversation(conversation)
        return self._conversations[username]

    def get_conversations(self):
        return self._conversations.values()

    def delete_conversation(self, username):
        if username not in self._conversations:
            raise ValueError('Conversation with user %s does not exist' %
                             username)
        # FIXME: delete or mark deleted?
        del self._conversations[username]

    def is_blocked(self, username):
        # FIXME: not implemented
        return False


@implementer(IInboxes)
class Inboxes(OOBTree):

    __parent__ = None

    def add_inbox(self, username):
        if username in self:
            raise ValueError('Inbox for user %s exists' % username)

        inbox = Inbox(username)
        self[username] = inbox
        return inbox

    def __setitem__(self, key, inbox):
        if not IInbox.providedBy(inbox):
            raise ValueError("Value '%s' does not provide IInbox" %
                             repr(inbox))
        if key != inbox.username:
            raise KeyError("Inbox username and key differ (%s/%s)" %
                           (inbox.username, key))
        inbox.__parent__ = self
        return super(Inboxes, self).__setitem__(key, inbox)


@implementer(IMessagingLocator)
class MessagingLocator(object):
    """A utility used to locate conversations and messages.
    """
