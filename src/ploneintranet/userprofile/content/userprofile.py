from plone import api as plone_api
from plone.app.textfield import RichText
from plone.dexterity.content import Container
from plone.directives import form
from plone.namedfile.field import NamedBlobImage
from z3c.form import validator
from zope import schema
from zope.interface import directlyProvides
from zope.interface import implementer
from zope.interface import Invalid
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary

from ploneintranet.userprofile import _


class IUserProfile(form.Schema):

    """User profile schema."""

    username = schema.TextLine(
        title=_(u"Username"),
        required=True
    )
    first_name = schema.TextLine(
        title=_(u"First name"),
        required=True
    )
    last_name = schema.TextLine(
        title=_(u"Last name"),
        required=True
    )
    email = schema.TextLine(
        title=_(u"Email"),
        required=True
    )


def primaryLocationVocabulary(context):
    # TODO: Locations should be stored in portal_registry for the time being.
    locations = [(u'L', u'London'), (u'P', u'Paris'), (u'B', u'Berlin')]
    terms = []
    for uid, title in locations:
        terms.append(SimpleVocabulary.createTerm(uid, str(uid), title))
    return SimpleVocabulary(terms)
directlyProvides(primaryLocationVocabulary, IContextSourceBinder)


class IUserProfileDefault(form.Schema):

    """User profile default schema."""

    telephone = schema.TextLine(
        title=_(u"Telephone Number"),
        required=True
    )
    mobile = schema.TextLine(
        title=_(u"Mobile Number"),
        required=True
    )
    time_zone = schema.TextLine(
        title=_(u"Time Zone"),
        required=True
    )
    primary_location = schema.Choice(
        title=_(u"Primary location"),
        source=primaryLocationVocabulary,
        required=True
    )
    biography = RichText(
        title=_(u"Biography"),
        required=True
    )
    photo = NamedBlobImage(
        title=_(u"Photo"),
        required=True
    )
    job_title = schema.TextLine(
        title=_(u"Job title"),
        required=True
    )
    department = schema.TextLine(
        title=_(u"Department"),
        required=True
    )


@implementer(IUserProfile)
class UserProfile(Container):

    """UserProfile content type."""

    pass


class UsernameValidator(validator.SimpleFieldValidator):

    """Two users can't have the same username."""

    def validate(self, value, force=False):
        membrane_tool = plone_api.portal.get_tool('membrane_tool')
        usernames = membrane_tool._catalog.uniqueValuesFor('exact_getUserName')
        if value in usernames:
            brains = membrane_tool.searchResults(exact_getUserName=value)
            if brains and self.context != brains[0].getObject():
                raise Invalid(_("A user with this username already exists"))

        return super(UsernameValidator, self).validate(value)


validator.WidgetValidatorDiscriminators(
    UsernameValidator,
    field=IUserProfile['username'])
