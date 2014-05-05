# -*- coding: utf-8 -*-
from zope import schema
from zope.interface import Attribute
from zope.interface import Interface


class IMessagingLocator(Interface):
    """A utility used to locate conversations and messages."""

    def get_inboxes():
        """Return an object providing IInboxes."""


class IInboxes(Interface):
    """Container holding inboxes."""

    def add_inbox(username):
        """Add an inbox for the user `username`. Returns the inbox."""

    def send_message(sender, recipient, text, created=None):
        """Send a message. This will create Inboxes, Conversations and
        Messages as needed.

        `sender` (:class:`unicode`)
            The sender's username.
        `recipient` (:class:`unicode`)
            The recipient's username.
        `text` (:class:`unicode`)
            The Text of the message.
        `created` (:class:`datetime.datetime`, optional)
            The creation date. If none is given, the current time will be used.

        Raises:
            `ValueError`
                If the user is blocked, sender and recipient are identical
                or the message has no text.

        Returns: `None`
        """

    def __getitem__(username):
        """Returns the inbox for the user `username`. Creates the inbox
        if it does not exist.
        """

    def __delitem__(username):
        """Delete an inbox."""


class IInbox(Interface):
    """An inbox for an user and the container for conversations."""

    # __parent__ = schema.Object(
    #     title=u"The parent `IInboxes' object"
    #     )

    new_messages_count = schema.Int(
        title=u'Number of unread messages in the inbox',
        required=True,
        default=0,
    )

    def add_conversation(conversation):
        """Add the conversation `conversation` to the inbox."""

    def __getitem__(username):
        """Get the conversation with the user `username`."""

    def __delitem__(username):
        """Delete the conversation the inbox user has with the user
        `username`.
        """

    def get_conversations():
        """Return all conversations stored in the inbox."""


class IConversation(Interface):
    """A conversation between the inbox user and another user.
    It contains the actual messages.
    """

    # __parent__ = schema.Object(
    #     title=u"The parent `IInbox' object"
    #     )

    username = schema.Text(
        title=u'The username of the other user (not the inbox user)'
    )

    new_messages_count = schema.Int(
        title=u'Number of unread messages in the conversation',
        required=True,
        default=0,
    )

    # probably not needed
    # last_updated = schema.Datetime(
    #     title=u'Date when the Conversation was last updated',
    #     missing_value=None,
    # )

    def get_messages():
        """Return all messages."""

    def add_message(message):
        """Add a message that provides `IMessage`."""

    def mark_read():
        """Mark the conversation and all contained messages as read."""

    def __getitem__(uid):
        """Return the message with the uid `uid`."""

    def __delitem__(uid):
        """Delete the message with the uid `uid`."""


class IMessage(Interface):
    """A message."""

    # __parent__ = schema.Object(
    #     title=u"The parent `IConversation' object"
    # )

    sender = schema.TextLine(
        title=u'Username of the sender'
    )

    recipient = schema.TextLine(
        title=u'Username of the recipient'
    )

    text = schema.Text(
        title=u'Text of the message'
    )

    created = schema.Datetime(
        title=u'Time the Message was created'
    )

    new = schema.Bool(
        title=u'Is the message read',
        default=False
    )

    uid = schema.Text(
        title=u'UUID unique within a conversation'
    )


class IMessagingTool(Interface):
    """Tool to store messages in the ZODB."""


class IMessageSendEvent(Interface):

    message = Attribute('The message Object')
