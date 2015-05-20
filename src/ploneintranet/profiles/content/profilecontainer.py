from plone.dexterity.content import Container
from plone.directives import form
from zope.interface import implementer


class IProfileContainer(form.Schema):
    """
    Marker interface for Profile
    """


@implementer(IProfileContainer)
class ProfileContainer(Container):
    """
    A folder to contain Profile
    """
