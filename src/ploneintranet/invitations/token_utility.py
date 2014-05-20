from zope.interface import implements
from zope.component import getUtility
from ploneintranet.invitations.interfaces import ITokenUtility
from ploneintranet.invitations.token import Token
from datetime import datetime
from datetime import timedelta
from zope.annotation.interfaces import IAnnotations
from BTrees.OOBTree import OOBTree

from Products.CMFCore.interfaces import ISiteRoot

ANNOTATION_KEY = "ploneintranet.invitations.token_storage"


class TokenUtility(object):
    """
    Utility to generate and consume tokens
    """
    implements(ITokenUtility)

    def generate_new_token(self, uses=None, expire_seconds=None):
        """
        Get a new unique token

        :param uses: The number of times this token is allowed to be consumed
                     before expiring
        :type uses: int
        :param expire_seconds: The number of seconds before this token expires
        :type expire_seconds: int
        :return: A token id
        :rtype: str
        """
        if expire_seconds is not None:
            expiry = datetime.now() + timedelta(seconds=expire_seconds)
        else:
            expiry = None
        token = Token(uses=uses, expiry=expiry)
        self._store_token(token)
        return token.id

    def remaining_uses(self, token_id):
        """
        Get the number of uses remaining for a given token

        :param token_id: The token id
        :type token_id: str
        :return: The number of uses remaining or None if this token no longer
                 exists
        :rtype: int
        """
        token = self._fetch_token(token_id)
        return token.uses

    def time_to_live(self, token_id):
        """
        Get the datetime of the expiry of a given token

        :param token_id: The token id
        :return: The seconds until token expires
        :rtype: int
        """
        token = self._fetch_token(token_id)
        ttl = token.expiry - datetime.now()
        if ttl < 0:
            return 0
        else:
            return ttl.total_seconds()
        pass

    def _consume_token(self, token_id):
        """
        Consume the given token and fire the event

        :param token_id: The token id
        :type token_id: str
        :return: Whether consumption succeeded or not. It will fail if the
                 token has expired
        :rtype: bool
        """
        token = self._fetch_token(token_id)
        pass

    def _fetch_token(self, token_id):
        """
        Get an existing token from the token storage

        :param token_id: A token id
        :type token_id: str
        :return: Token object
        """
        storage = self._get_storage()
        return storage.get(token_id)

    def _store_token(self, token):
        """
        Store a token in the token storage

        :param token: A token
        :type token: Token
        """
        storage = self._get_storage()
        storage[token.id] = token

    def _get_storage(self, clear=False):
        """
        Look up storage for tokens

        :param clear: Force clear the storage
        :type clear: bool
        :return: Token storage
        """
        portal = getUtility(ISiteRoot)
        annotations = IAnnotations(portal)
        if ANNOTATION_KEY not in annotations or clear:
            annotations[ANNOTATION_KEY] = OOBTree()
        return annotations[ANNOTATION_KEY]
