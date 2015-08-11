from zope.interface import Interface, Attribute
from ploneintranet.core import ploneintranetCoreMessageFactory as _  # noqa


class IPloneintranetInvitationsLayer(Interface):
    """Marker interface that defines a Zope 3 browser layer."""


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
    id = Attribute(_('The UUID of this token'))
    uses = Attribute(_('The number of uses for this token before it expires'))
    expiry = Attribute(_('The datetime this token expires'))
