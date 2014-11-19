from zope.interface import Interface


class INotificationsQueue(Interface):
    """
    Don't know what it stores yet.
    """

class INotificationsTool(Interface):
    """
    Provide INotificationsQueue as a site utility
    """
