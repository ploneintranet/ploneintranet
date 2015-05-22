from datetime import datetime
from datetime import timedelta

from zope.interface import implements
from zope.component import getUtility
from zope.annotation.interfaces import IAnnotations
from BTrees.OOBTree import OOBTree
from Products.CMFCore.interfaces import ISiteRoot

from ploneintranet.invitations.interfaces import ITokenUtility
from ploneintranet.invitations.token import Token


ANNOTATION_KEY = 'ploneintranet.invitations.token_storage'


class TokenUtility(object):
    """
    Utility to generate and consume tokens
    """
    implements(ITokenUtility)

    def generate_new_token(self, usage_limit=1, expire_seconds=None,
                           redirect_path=None):
        """
        Get a new unique token

        :param usage_limit: The number of times this token is allowed to be
                            consumed before expiring
        :type usage_limit: int, default 1. None for unlimited use.
        :param expire_seconds: The number of seconds before this token expires
        :type expire_seconds: int
        :param redirect_path: The optional path to redirect to, relative to the
                              Plone site, after token is accepted
        :type redirect_path: str
        :return: A tuple containing the id of the generated token
                 and a url that can be used to accept the token
        :rtype: (token_id, token_url)
        """
        if expire_seconds is not None:
            expiry = datetime.now() + timedelta(seconds=expire_seconds)
        else:
            expiry = datetime.max
        token = Token(
            usage_limit=usage_limit,
            expiry=expiry,
            redirect_path=redirect_path
        )
        self._store_token(token)
        return token.id, token.invite_url

    def valid(self, token_id):
        """
        Has the token with the given id expired?

        :return: Whether or not the token has expired
        :rtype: bool
        """
        token = self._fetch_token(token_id)
        if token is None:
            return False
        usage_allowed = (token.uses_remaining is None
                         or token.uses_remaining > 0)
        in_date = token.expiry > datetime.now()
        return usage_allowed and in_date

    def _consume_token(self, token_id):
        """
        Consume the given token and fire the event

        :param token_id: The token id
        :type token_id: str
        :return: Whether consumption succeeded or not. It will fail if the
                 token has expired
        :rtype: bool
        """
        if not self.valid(token_id):
            return False
        token = self._fetch_token(token_id)
        if token.uses_remaining is not None:
            token.uses_remaining -= 1
        return True

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
