import os
from zope.interface import Attribute, Interface


API_KEY = os.environ['GCM_API_KEY']

SENDER_ID = os.environ['GCM_SENDER_ID']


class IGCMService(Interface):

    context = Attribute(u'The user profile object.')

    def push_status_update(self, status_update, message):
        """Send a push notifications to users mentioned in a status update message.

        This method should log any exceptions encountered, but not raise.

        :param status_update: THe status update.
        :type status_update: ploneintranet.microblog.interfaces.IStatusUpdate
        :param message: The message instance.
        :type message: ploneintranet.messaging.messaging.IMessage
        :return: Nothing
        """


class ITokenAssociation(Interface):

    context = Attribute(u'The user profile object.')
    request = Attribute(u'The request.')

    def save(token):
        """Obtain a token obtained from the request
        and store aginst the user profile.

        :param token: The GCM registration token.
        :type token: str
        :raise: ValueError if the token cannot be obtained.
        """

    def remove():
        """Remove token associate from the user profile."""
