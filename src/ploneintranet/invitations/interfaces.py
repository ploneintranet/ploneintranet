from zope.interface import Interface


class ITokenUtility(Interface):
    """ Interface for the TokenUtility
    """
    def get_new_token(self):
        pass

    def get_uses(self, token):
        pass

    def get_expiry(self, token):
        pass