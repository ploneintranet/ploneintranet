# -*- coding: utf-8 -*-
from BTrees.LOBTree import LOBTree
from BTrees.OOBTree import OOBTree
from Persistence import Persistent
from Products.CMFPlone.utils import getToolByName
from datetime import datetime
from plonesocial.messaging.interfaces import IConversation
from plonesocial.messaging.interfaces import IInbox
from plonesocial.messaging.interfaces import IInboxes
from plonesocial.messaging.interfaces import IMessage
from plonesocial.messaging.interfaces import IMessagingLocator
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.interface.verify import verifyObject

import time


@implementer(IMessage)
class Message(Persistent):

    __parent__ = None

    sender = None
    recipient = None
    text = None
    created = None
    uuid = None
    new = True

    def __init__(self, sender, recipient, text, created):
        if sender == recipient:
            msg = 'Sender and recipient are identical ({0}, {1})'
            raise ValueError(msg.format(sender, recipient))  # FIXME: test
        if not text.strip():
            raise ValueError('Message has no text')  # FIXME: test

        self.sender = sender
        self.recipient = recipient
        self.text = text
        self.created = created


@implementer(IConversation)
class Conversation(LOBTree):

    __parent__ = None

    username = None
    last_updated = None
    new_messages_count = 0

    def __init__(self, username, created):
        self.username = username
        self.last_updated

    def to_long(self, dt):
        """Turns a `datetime` object into a long."""
        return long(time.mktime(dt.timetuple()) * 1000000 + dt.microsecond)

    def generate_key(self, message):
        """Generate a long int key for a message."""
        key = self.to_long(message.created)
        while key in self:
            key = key + 1
        return key

    def add_message(self, message):
        key = self.generate_key(message)
        message.uid = key
        self[key] = message
        return key

    def __setitem__(self, key, message):
        if key != message.uid:
            msg = 'key and message.uid differ ({0}/{1})'
            raise KeyError(msg.format(key, message.uid))
        message.__parent__ = self

        # delete old message if there is one to make sure the
        # new_messages_count is correct and update the new_messages_count
        # with the new message
        if key in self:
            del self[key]
        if message.new is True:
            self.update_new_messages_count(+1)

        super(Conversation, self).__setitem__(key, message)

    def __delitem__(self, uid):
        message = self[uid]
        if message.new is True:
            self.update_new_messages_count(-1)
        super(Conversation, self).__delitem__(uid)

    def get_messages(self):
        return self.values()

    def mark_read(self):
        # use update function to update inbox too
        self.update_new_messages_count(self.new_messages_count * -1)

        # update messages
        for message in self.values():
            message.new = False

    def update_new_messages_count(self, difference):
        count = self.new_messages_count
        count = count + difference
        if count < 0:
            # FIXME: Error. Log?
            count = 0
        self.new_messages_count = count

        # update the inbox accordingly
        self.__parent__.update_new_messages_count(difference)


@implementer(IInbox)
class Inbox(OOBTree):

    __parent__ = None

    username = None
    new_messages_count = 0

    def __init__(self, username):
        self.username = username

    def add_conversation(self, conversation):
        self[conversation.username] = conversation
        return conversation

    def __setitem__(self, key, conversation):
        if key != conversation.username:
            msg = 'conversation.username and key differ ({0}, {1})'
            raise KeyError(msg.format(conversation.username, key))

        if conversation.username == self.username:
            raise ValueError("You can't speak to yourself")

        verifyObject(IConversation, conversation)

        if key in self:
            raise KeyError('Conversation exists already')

        super(Inbox, self).__setitem__(conversation.username, conversation)
        conversation.__parent__ = self
        self.update_new_messages_count(conversation.new_messages_count)
        return conversation

    def __delitem__(self, key):
        conversation = self[key]
        self.update_new_messages_count(conversation.new_messages_count * -1)
        super(Inbox, self).__delitem__(key)

    def get_conversations(self):
        return self.values()

    def is_blocked(self, username):
        # FIXME: not implemented
        return False

    def update_new_messages_count(self, difference):
        count = self.new_messages_count
        count = count + difference
        if count < 0:
            # FIXME: Error. Log?
            count = 0
        self.new_messages_count = count


@implementer(IInboxes)
class Inboxes(OOBTree):

    __parent__ = None

    def add_inbox(self, username):
        if username in self:
            raise ValueError('Inbox for user {0} exists'.format(username))

        inbox = Inbox(username)
        self[username] = inbox
        return inbox

    def __setitem__(self, key, inbox):
        verifyObject(IInbox, inbox)
        if key != inbox.username:
            msg = 'Inbox username and key differ ({0}/{1})'
            raise KeyError(msg.format(inbox.username, key))
        inbox.__parent__ = self

        # outside tests we need to remove the acquisition wrapper
        unwrapped_self = self.aq_base if hasattr(self, 'aq_base') else self
        return super(Inboxes, unwrapped_self).__setitem__(key, inbox)

    def send_message(self, sender, recipient, text, created=None):
        if not sender in self:
            self.add_inbox(sender)
        sender_inbox = self[sender]
        if not recipient in self:
            self.add_inbox(recipient)
        recipient_inbox = self[recipient]

        if recipient_inbox.is_blocked('sender'):
            # FIXME: Own Exception or security exception?
            raise ValueError('User is not allowed to send a Message to '
                             'the Recipient')

        if created is None:
            # FIXME: or utcnow?
            created = datetime.now()

        for pair in ((sender_inbox, recipient),
                     (recipient_inbox, sender)):
            inbox = pair[0]
            conversation_user = pair[1]
            if conversation_user not in inbox:
                inbox.add_conversation(Conversation(conversation_user,
                                                    created))
            conversation = inbox[conversation_user]
            message = Message(sender, recipient, text, created)
            conversation.add_message(message)


@implementer(IMessagingLocator)
class MessagingLocator(object):
    """A utility used to locate conversations and messages."""

    def get_inboxes(self):
        site = getSite()
        return getToolByName(site, 'plonesocial_messaging')
