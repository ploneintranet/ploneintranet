
class TokenUtility(object):
    """
    Utility to generate and consume tokens
    """
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

    def get_uses(self, token):
        """
        Get the number of uses remaining for a given token

        :param token: The token hash
        :type token: str
        :return: The number of uses remaining or None if this token no longer
                 exists
        :rtype: int
        """
        pass

    def get_expiry(self, token):
        """
        Get the datetime of the expiry of a given token

        :param token: The token hash
        :return: The datetime of expiry
        :rtype: datetime
        """
        pass

    def _consume_token(self, token):
        """
        Consume the given token and fire the event

        :param token: The token hash
        :type token: str
        :return: Whether consumption succeeded or not. It will fail if the
                 token has expired
        :rtype: bool
        """
        pass

    def _get_token(self, token):
        """
        Fetch token from storage

        :param token: A token hash
        :type token: str
        :return: Token object
        """
        pass