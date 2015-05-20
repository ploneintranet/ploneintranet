from zope import schema
from zope.interface import implementer

from plone.dexterity.content import Container
from plone.directives import form

from ploneintranet.userprofile import _


class IUserProfile(form.Schema):

    """User profile schema."""

    first_name = schema.TextLine(
        title=_("First name"),
        required=True
    )

    last_name = schema.TextLine(
        title=_("Last name"),
        required=True
    )

    email = schema.TextLine(
        title=_("Email"),
        required=True
    )


@implementer(IUserProfile)
class UserProfile(Container):

    """UserProfile content type."""

    pass
