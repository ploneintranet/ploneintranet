from zope.interface import Interface, Attribute


class ITokenUtility(Interface):
    """ Interface for the TokenUtility
    """
    def generate_new_token(self):
        """
        Get a new unique token
        """

    def valid(self, token_id):
        """
        Is the token for given id still valid
        """


class IToken(Interface):
    """ Interface for Token class
    """
    id = Attribute('The UUID of this token')
    uses = Attribute('The number of uses for this token before it expires')
    expiry = Attribute('The datetime this token expires')
