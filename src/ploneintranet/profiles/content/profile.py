from zope import schema
from zope.interface import implementer

from plone.dexterity.content import Container
from plone.directives import form

from ploneintranet.profiles import _


class IProfile(form.Schema):

    """Profile schema."""

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


@implementer(IProfile)
class Profile(Container):

    """Profile content type."""

    pass
