from zope.component.interfaces import IObjectEvent, ObjectEvent
from zope.interface import implements


class ITokenConsumed(IObjectEvent):
    pass


class TokenConsumed(ObjectEvent):
    """
    Event to be fired whenever a token is consumed
    """
    implements(ITokenConsumed)

    def __init__(self, obj):
        super(TokenConsumed, self).__init__(obj)
