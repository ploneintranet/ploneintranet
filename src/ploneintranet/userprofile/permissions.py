from zope.component import adapts
from zope.interface import implements
from borg.localrole.default_adapter import DefaultLocalRoleAdapter
from borg.localrole.interfaces import ILocalRoleProvider
from Products.membrane.interfaces import IMembraneUserObject

from ploneintranet.userprofile.content.userprofile import IUserProfile


class UserProfileLocalRoleAdapter(DefaultLocalRoleAdapter):
    """
    User's get 'Owner' on their own user profile
    """
    implements(ILocalRoleProvider)
    adapts(IUserProfile)

    def getRoles(self, principal_id):
        """
        give an Owner who is also a 'selfpublisher', the reviewer role
        """
        context = self.context
        current_roles = list(DefaultLocalRoleAdapter.getRoles(
            self,
            principal_id,
        ))

        userid = IMembraneUserObject(context).getUserId()
        if principal_id == userid:
            current_roles.append('Owner')

        return current_roles
