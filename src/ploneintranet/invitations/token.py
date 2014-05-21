from uuid import uuid4
from persistent import Persistent


class Token(Persistent):
    """
    Definition of a token object
    """
    def __init__(self, usage_limit, expiry):
        self.uses_remaining = usage_limit
        self.expiry = expiry
        self.id = uuid4().hex
