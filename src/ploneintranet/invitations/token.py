from uuid import uuid4
from persistent import Persistent
from plone import api


class Token(Persistent):
    """
    Definition of a token object
    """
    def __init__(self, usage_limit, expiry):
        self.uses_remaining = usage_limit
        self.expiry = expiry
        self.id = uuid4().hex

    @property
    def invite_url(self):
        portal_url = api.portal.get().absolute_url()
        return '%s/@@accept-token/%s' % (
            portal_url,
            self.id,
        )
