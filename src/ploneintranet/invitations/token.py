from uuid import uuid4
from persistent import Persistent
from plone import api
from zope.interface import implements

from .interfaces import IToken


class Token(Persistent):
    """
    Definition of a token object

    :ivar uses_remaining: (`int`) The number of uses remaining for this token
                          before expiry
    :ivar expiry: (:class:`datetime`) The `datetime` this token will expire
    :ivar id: (:class:`uuid.uuid4`) The unique identifier of this token
    :ivar redirect_path: (`str`) The optional path to redirect to after
                         the token is accepted
    """
    implements(IToken)

    def __init__(self, usage_limit, expiry, redirect_path=None):
        self.uses_remaining = usage_limit
        self.expiry = expiry
        self.id = uuid4().hex
        self.redirect_path = redirect_path

    @property
    def invite_url(self):
        """
        The invitation URL of this token
        """
        portal_url = api.portal.get().absolute_url()
        return '%s/@@accept-token/%s' % (
            portal_url,
            self.id,
        )
