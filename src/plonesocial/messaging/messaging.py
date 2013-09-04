from plonesocial.messaging.interfaces import IMessagingLocator
from zope.interface import implements


class MessagingLocator(object):
    """A utility used to locate conversations and messages.
    """

    implements(IMessagingLocator)
