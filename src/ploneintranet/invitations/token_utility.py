from zope.interface import implements
from ploneintranet.invitations.interfaces import ITokenUtility


class TokenUtility(object):
    """
    Utility to generate and consume tokens
    """
    implements(ITokenUtility)

    def generate_new_token(self, uses=1, expiry=300):
        """
        Get a new unique token

        :param uses: The number of times this token is allowed to be consumed
                     before expiring
        :type uses: int
        :param expiry: The number of seconds before this token expires
        :type expiry: int
        :return: A token id
        :rtype: str
        """
        pass

    def remaining_uses(self, token_id):
        """
        Get the number of uses remaining for a given token

        :param token_id: The token id
        :type token_id: str
        :return: The number of uses remaining or None if this token no longer
                 exists
        :rtype: int
        """
        token = self._get_token(token_id)
        pass

    def time_to_live(self, token_id):
        """
        Get the datetime of the expiry of a given token

        :param token_id: The token id
        :return: The datetime of expiry
        :rtype: datetime
        """
        token = self._get_token(token_id)
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
        token = self._get_token(token_id)
        pass

    def _get_token(self, token_id):
        """
5
        :param token_id: A token id
        :type token_id: str
        :return: Token object
        """
        pass