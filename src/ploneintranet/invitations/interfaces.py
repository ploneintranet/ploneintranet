from zope.interface import Interface


class ITokenUtility(Interface):
    """ Interface for the TokenUtility
    """
    def generate_new_token(self):
        """
        Get a new unique token
        """

    def remaining_uses(self, token):
        """
        Get uses remaining of the given token
        """

    def time_to_live(self, token):
        """
        Get the datetime of expiry of the given token
        """
