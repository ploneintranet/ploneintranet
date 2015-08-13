import os
from zope.interface import Attribute, Interface


API_KEY = os.environ['GCM_API_KEY']

SENDER_ID = os.environ['GCM_SENDER_ID']


class IGCMService(Interface):

    context = Attribute(u'The user profile object.')

    def send_push_notifications(message):
        """Send a push notification message to the user.

        This method log any exceptions encountered.

        :param message: The message instance.
        :type message: ploneintranet.messaging.messaging.IMessage
        :return: Nothing
        """
