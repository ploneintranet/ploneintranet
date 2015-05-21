from zope import schema
from zope.interface import implementer
from zope.interface import Invalid
from z3c.form import validator

from plone import api as plone_api
from plone.dexterity.content import Container
from plone.directives import form

from ploneintranet.userprofile import _


class IUserProfile(form.Schema):

    """User profile schema."""

    username = schema.TextLine(
        title=_("Username"),
        required=True
    )

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


class UsernameValidator(validator.SimpleFieldValidator):

    """Two users can't have the same username."""

    def validate(self, value):
        super(UsernameValidator, self).validate(value)
        membrane_tool = plone_api.portal.get_tool('membrane_tool')
        brains = membrane_tool.searchResults(
            username=value,
            portal_type='ploneintranet.userprofile.userprofile')
        if brains:
            raise Invalid(_("A user with this username already exists"))


validator.WidgetValidatorDiscriminators(
    UsernameValidator,
    field=IUserProfile['username'])
