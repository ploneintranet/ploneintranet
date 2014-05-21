from zope.interface import Attribute
from zope.interface import Interface
from zope.interface import implements


class ITokenConsumed(Interface):

    token_id = Attribute("The id of the Token that was consumed")


class TokenConsumed(object):
    """
    Event to be fired whenever a token is consumed
    """
    implements(ITokenConsumed)

    def __init__(self, token_id):
        self.token_id = token_id
