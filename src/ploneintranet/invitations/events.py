from zope.interface import Attribute
from zope.interface import Interface
from zope.interface import implements


class ITokenAccepted(Interface):

    token_id = Attribute("The id of the Token that was consumed")


class TokenAccepted(object):
    """
    Event to be fired whenever a token is consumed
    """
    implements(ITokenAccepted)

    def __init__(self, token_id):
        self.token_id = token_id
