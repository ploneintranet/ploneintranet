from zope.interface import implements
from .interfaces import ITokenUtility


class TokenUtility(object):
    """
    Utility to generate and consume tokens
    """
    implements(ITokenUtility)

    def get_new_token(self, uses=1, expiry=300):
        """
        Get a new unique token

        :param uses: The number of times this token is allowed to be consumed
                     before expiring
        :type uses: int
        :param expiry: The number of seconds before this token expires
        :type expiry: int
        :return: A token hash
        :rtype: str
        """
        pass

    def get_uses(self, hash_str):
        """
        Get the number of uses remaining for a given token

        :param hash_str: The token hash
        :type hash_str: str
        :return: The number of uses remaining or None if this token no longer
                 exists
        :rtype: int
        """
        token = self._get_token(hash_str)
        pass

    def get_expiry(self, hash_str):
        """
        Get the datetime of the expiry of a given token

        :param hash_str: The token hash
        :return: The datetime of expiry
        :rtype: datetime
        """
        token = self._get_token(hash_str)
        pass

    def _consume_token(self, hash_str):
        """
        Consume the given token and fire the event

        :param hash_str: The token hash
        :type hash_str: str
        :return: Whether consumption succeeded or not. It will fail if the
                 token has expired
        :rtype: bool
        """
        token = self._get_token(hash_str)
        pass

    def _get_token(self, hash_str):
        """
        Fetch token from storage

        :param hash_str: A token hash
        :type hash_str: str
        :return: Token object
        """
        pass