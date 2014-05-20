from uuid import uuid4
from persistent import Persistent


class Token(Persistent):
    """
    Definition of a token object
    """
    def __init__(self, uses, expiry):
        self.uses = uses
        self.expiry = expiry
        self.id = uuid4().hex