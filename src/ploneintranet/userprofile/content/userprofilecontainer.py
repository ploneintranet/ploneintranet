from plone.dexterity.content import Container
from plone.directives import form
from zope.interface import implementer


class IUserProfileContainer(form.Schema):
    """
    Marker interface for Profile
    """


@implementer(IUserProfileContainer)
class UserProfileContainer(Container):
    """
    A folder to contain Profile
    """
