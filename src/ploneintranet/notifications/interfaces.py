# -*- coding: utf-8 -*-

from zope.interface import Interface


class INotificationsQueues(Interface):
    """
    Stores queues for notifications for each user.
    Queues are implemented with PersistentLists and can be modified in place.
    On first request for users not having queues yet, an empty queue gets
    generated automatically.
    """

    def clear(self):
        """Empty all queues"""

    def get_user_queue(self, userid):
        """
        Get a queue for given userid.
        Create and return a new persistent queue if user did not have
        a queue yet.
        """

    def del_user_queue(self, userid):
        """
        Delete the queue for the given userid.
        """


class IMessage(Interface):
    """
    Represents a Notification Message for a specific user
    """


class INotificationsTool(Interface):
    """
    Provide INotificationsQueue as a site utility
    """
