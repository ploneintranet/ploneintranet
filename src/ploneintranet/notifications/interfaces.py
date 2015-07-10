# -*- coding: utf-8 -*-

from zope.interface import Interface


class INotificationsTool(Interface):
    """
    Provide INotificationsQueue as a site utility
    For package internal use only
    """


class INotificationsQueues(Interface):
    """
    Stores queues for notifications for each user.
    Queues are implemented with PersistentLists and can be modified in place.
    On first request for users not having queues yet, an empty queue gets
    generated automatically.
    You interact with queues via Channels and MessageClassHandlers
    """

    def clear(self):
        """Empty all queues"""

    def get_user_queue(self, userid):
        """
        Get a queue for given user object.
        Create and return a new persistent queue if user did not have
        a queue yet.
        """

    def del_user_queue(self, userid):
        """
        Delete the queue for the given user object.
        """


class IChannel(Interface):
    """
    Represents an access to message queues for consumption.
    It is responsible to filtering the message queue so that
    not all types of messages are being shown.
    It is also responsible for updating the read flags as
    required.
    To add messages, use a MessageClassHandler

    If you need unfiltered access, use
    :class:`ploneintranet.notifications.channel.AllChannel`
    """
    def get_unread_count(self):
        """
        Return the unread message count, filtered for messages this
        Channel would return anyway
        """

    def get_unread_messages(self, keep_unread=False):
        """
        Return the unread messages, filtered for messages this
        Channel would return anyway.
        By default, this will also mark the messages as read.
        You can change this behavior by setting ``keep_unread`` to True
        """

    def get_all_messages(self):
        """
        Return read and unread messages, filtered for messages this
        Channel would not return anyway
        You can limit the number of messages to return with the
        ``limit`` argument
        """


class IMessageClassHandler(Interface):
    """
    Represents a handler that creates message for each user
    who should get them. Does not handle message access, does
    not manage, where to show the message.
    Since this is an expensive operation, this handler API
    might change in the future to facilitate batching
    or asynchronous handling. Nothing official so far though
    It is the MessageClassHandler responsability to only look
    for messages it is really responsible for.
    """

    def add(self, message):
        """
        Add a message to each user who should get the message.
        The message gets cloned
        """

    def cleanup(self):
        """
        Checks for each user if relevant messages should be deleted
        """


class IMessage(Interface):
    """
    Represents a Notification Message for a specific userw
    """
    def mark_as_read(now=None):
        """
        Mark the message as read.
        if ``now`` is provided, it is assumed as an utc timestamp
        and stored
        """

    def marked_read_as():
        """
        Return when the message has been read as an utc time stamp
        """

    def is_unread(self):
        """
        Return whether the message is unread
        """

    def clone(self):
        """
        Return a clone of the message
        """

    def update_object(self, obj):
        """
        Update the object.
        Forces an update of the ``message_last_modification_date``
        which is stored on the object
        """

    def update_actors(self, added=[], removed=[]):
        """
        Update the actors list
        """


class INotifiable(Interface):
    """
    Interface applied to objects that should be notified
    """


class IMessageFactory(Interface):
    """
    Creates a message
    """
