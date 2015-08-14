from zope.interface import implementer

from .interfaces import ITokenAssociation
from .util import read_token


@implementer(ITokenAssociation)
class TokenAssociator(object):
    """Associate a token with a userprofile."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def save(self, token):
        response = self.request.response
        try:
            token = read_token(self.request)
        except ValueError:
            response.setStatus('BadRequest')
        else:
            self.context.gcm_reg_id = token.encode('ascii')

    def remove(self):
        self.context.gcm_reg_id = None
