import os
from zope.interface import Attribute, Interface


API_KEY = os.environ['GCM_API_KEY']

SENDER_ID = os.environ['GCM_SENDER_ID']


class IGCMService(Interface):

    context = Attribute(u'The user')

    def send_push_notification(message):
        """Send a push notification message to the user."""


class IUserPushNotificationsOptIn(Interface):
    """A behavior that Adapts a membrane user.

    Allows users to Opt in to GCM push notifications.
    """

    def is_registered():
        """Return true iif this user is registered with GCM."""
