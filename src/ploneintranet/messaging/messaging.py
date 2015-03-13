# -*- coding: utf-8 -*-
from BTrees.LOBTree import LOBTree
from BTrees.OOBTree import OOBTree
from Persistence import Persistent
from datetime import datetime
from plone import api
from ploneintranet.messaging.events import MessageSendEvent
from ploneintranet.messaging.interfaces import IConversation
from ploneintranet.messaging.interfaces import IInbox
from ploneintranet.messaging.interfaces import IInboxes
from ploneintranet.messaging.interfaces import IMessage
from ploneintranet.messaging.interfaces import IMessagingLocator
from zope.event import notify
from zope.interface import implementer
from zope.interface.verify import verifyObject
import time


class BTreeDictBase(Persistent):
    '''Pass through the dict api to a BTree saved in self.data
    This is required cause attributes on **BTree subclasses
    seem to not be persistent. It also takes care to set a __parent__
    pointer
    '''

    __parent__ = None

    def __setitem__(self, key, value):
        value.__parent__ = self
        return self.data.__setitem__(key, value)

    def __getitem__(self, key):
        return self.data.__getitem__(key)

    def __contains__(self, key):
        return self.data.__contains__(key)

    def __delitem__(self, key):
        return self.data.__delitem__(key)

    def keys(self):
        return self.data.keys()


@implementer(IMessage)
class Message(Persistent):

    __parent__ = None

    sender = None
    recipient = None
    text = None
    created = None
    uid = None
    new = True

    def __init__(self, sender, recipient, text, created):
        if sender == recipient:
            msg = 'Sender and recipient are identical ({0}, {1})'
            raise ValueError(msg.format(sender, recipient))  # FIXME: test
        if not text.strip():
            raise ValueError('Message has no text')  # FIXME: test
        if not isinstance(created, datetime):
            raise ValueError('created has to be a datetime object')
        self.sender = sender
        self.recipient = recipient
        self.text = text
        self.created = created

    def to_dict(self):
        return dict(sender=self.sender,
                    recipient=self.recipient,
                    text=self.text,
                    created=self.created,
                    new=self.new,
                    uid=self.uid)


@implementer(IConversation)
class Conversation(BTreeDictBase):

    username = None
    new_messages_count = 0
    created = None

    def __init__(self, username, created):
        self.data = LOBTree()
        self.username = username
        self.created = created

    def to_long(self, dt):
        """Turns a `datetime` object into a long."""
        return long(time.mktime(dt.timetuple()) * 1000000 + dt.microsecond)

    def generate_key(self, message):
        """Generate a long int key for a message."""
        key = self.to_long(message.created)
        while key in self.data:
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
        return self.data.values()

    def mark_read(self):
        # use update function to update inbox too
        self.update_new_messages_count(self.new_messages_count * -1)

        # update messages
        for message in self.data.values():
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

    def to_dict(self):
        member = api.user.get(self.username)
        return {'username': self.username,
                'fullname': member.getProperty('fullname'),
                'new_messages_count': self.new_messages_count}


@implementer(IInbox)
class Inbox(BTreeDictBase):

    username = None
    new_messages_count = 0

    def __init__(self, username):
        self.data = OOBTree()
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
        self.update_new_messages_count(conversation.new_messages_count)
        return conversation

    def __delitem__(self, key):
        conversation = self[key]
        self.update_new_messages_count(conversation.new_messages_count * -1)
        super(Inbox, self).__delitem__(key)

    def get_conversations(self):
        return self.data.values()

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
class Inboxes(BTreeDictBase):

    def __init__(self):
        self.data = OOBTree()

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

        # outside tests we need to remove the acquisition wrapper
        # unwrapped_self = self.aq_base if hasattr(self, 'aq_base') else self
        return BTreeDictBase.__setitem__(self, key, inbox)
        # return super(Inboxes, unwrapped_self).__setitem__(key, inbox)

    def send_message(self, sender, recipient, text, created=None):
        if sender not in self:
            self.add_inbox(sender)
        sender_inbox = self[sender]
        if recipient not in self:
            self.add_inbox(recipient)
        recipient_inbox = self[recipient]

        if recipient_inbox.is_blocked('sender'):
            # FIXME: Own Exception or security exception?
            raise ValueError('User is not allowed to send a Message to '
                             'the Recipient')

        if created is None:
            # FIXME: or utcnow?
            created = datetime.now()

        for pair in ((sender_inbox, recipient, False),
                     (recipient_inbox, sender, True)):
            inbox = pair[0]
            conversation_user = pair[1]
            if conversation_user not in inbox:
                inbox.add_conversation(Conversation(conversation_user,
                                                    created))
            conversation = inbox[conversation_user]
            message = Message(sender, recipient, text, created)
            conversation.add_message(message)
            send_event = pair[2]
            if send_event:
                event = MessageSendEvent(message)
                notify(event)


@implementer(IMessagingLocator)
class MessagingLocator(object):
    """A utility used to locate conversations and messages."""

    def get_inboxes(self):
        return api.portal.get_tool('ploneintranet_messaging')
