from zope.interface import Interface
from zope import schema


class IMessagingLocator(Interface):
    """A utility used to locate conversations and messages.
    """


class IInboxes(Interface):
    """Container holding inboxes"""

    def add_inbox(username):
        """Add an inbox for the user `username`. Returns the inbox"""

    def __getitem__(username):
        """
        Returns the inbox for the user `username`. Creates the inbox
        if it does not exist.
        """

    def __setitem__(username, inbox):
        """
        Use add_inbox instead create an inbox.
        
        Adds an inbox for the user `username`. 
        Raises `KeyError` if the `username` and the `inbox.username` differ.
        Raises `ValueError` if the inbox does not provide `IInbox`
        """

    def __delitem__(username):
        """
        Delete an inbox.
        """


class IInbox(Interface):
    """An inbox for an user and the container for conversations"""

    # __parent__ = schema.Object(
    #     title=u"The parent `IInboxes' object"
    #     )

    def add_conversation(conversation):
        """
        Adds the conversation `conversation` to the inbox.
        """

    def get_conversation(username):
        """
        Returns the conversation the inbox user has with the user
        `username`.
        """

    def delete_conversation(username):
        """
        Delete the conversation the inbox user has with the user `username`.
        FIXME: Mark deleted or remove?
        """

    def get_conversations():
        """
        Return all conversations stored in the inbox
        """


class IConversation(Interface):
    """
    A conversation between the inbox user and another user.
    It contains the actual messages.
    """

    # __parent__ = schema.Object(
    #     title=u"The parent `IInbox' object"
    #     )

    username = schema.Text(
        title=u"The username of the other user (not the inbox user)"
        )

    unread_messages_count = schema.Int(
        title=u'Number of unread messages in the conversation',
        required=True,
        default=0,
        )

    last_updated = schema.Datetime(
        title=u'Date when the Conversation was last updated',
        missing_value=None,
        )

    def get_messages():
        """return all messages"""

    def add_message(message):
        """Add a message that provides `IMessage`"""

    def mark_read():
        """Mark the conversation and all contained messages read"""


class IMessage(Interface):
    """A message"""

    # __parent__ = schema.Object(
    #     title=u"The parent `IConversation' object"
    #     )

    sender = schema.Text(
        title=u"Username of the sender"
        )

    recipient = schema.Text(
        title=u"Username of the recipient"
        )

    sender = schema.Text(
        title=u"Text of the message"
        )

    created = schema.Datetime(
        title=u"Time the Message was created"
        )

    deleted = schema.Datetime(
        title=u"Time the Message was deleted",
        default=None
        )

    read = schema.Bool(
        title=u"Is the message read",
        default=False
        )

    uid = schema.Text(
        title=u"UUID unique within a conversation"
        )
