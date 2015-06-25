from z3c.form import validator
from zope import schema
from zope.interface import alsoProvides
from zope.interface import directlyProvides
from zope.interface import implementer
from zope.interface import Invalid
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
from collective import dexteritytextindexer

from plone import api as plone_api
from plone.autoform.interfaces import IFormFieldProvider
from plone.app.textfield import RichText
from plone.dexterity.content import Container
from plone.directives import form
from plone.namedfile.field import NamedBlobImage

from ploneintranet.userprofile import _


class IUserProfile(form.Schema):

    """The core user profile schema.

    Most of the plone intranet UI relies on these fields.
    """

    dexteritytextindexer.searchable('username')
    username = schema.TextLine(
        title=_(u"Username"),
        required=True
    )
    dexteritytextindexer.searchable('first_name')
    first_name = schema.TextLine(
        title=_(u"First name"),
        required=True
    )
    dexteritytextindexer.searchable('last_name')
    last_name = schema.TextLine(
        title=_(u"Last name"),
        required=True
    )
    dexteritytextindexer.searchable('email')
    email = schema.TextLine(
        title=_(u"Email"),
        required=True
    )
    portrait = NamedBlobImage(
        title=_(u"Photo"),
        required=False
    )


def primaryLocationVocabulary(context):
    # TODO: Locations should be stored in portal_registry for the time being.
    locations = [(u'L', u'London'), (u'P', u'Paris'), (u'B', u'Berlin')]
    terms = []
    for uid, title in locations:
        terms.append(SimpleVocabulary.createTerm(uid, str(uid), title))
    return SimpleVocabulary(terms)
directlyProvides(primaryLocationVocabulary, IContextSourceBinder)


class IUserProfileAdditional(form.Schema):

    """Default additional fields for UserProfile."""

    person_title = schema.TextLine(
        title=_(u"Person title"),
        required=False
    )
    telephone = schema.TextLine(
        title=_(u"Telephone Number"),
        required=False
    )
    mobile = schema.TextLine(
        title=_(u"Mobile Number"),
        required=False
    )
    time_zone = schema.TextLine(
        title=_(u"Time Zone"),
        required=False
    )
    primary_location = schema.Choice(
        title=_(u"Primary location"),
        source=primaryLocationVocabulary,
        required=False
    )
    biography = RichText(
        title=_(u"Biography"),
        required=False
    )
    job_title = schema.TextLine(
        title=_(u"Job title"),
        required=False
    )
    department = schema.TextLine(
        title=_(u"Department"),
        required=False
    )


alsoProvides(IUserProfileAdditional, IFormFieldProvider)


@implementer(IUserProfile)
class UserProfile(Container):

    """UserProfile content type."""

    def Title(self):
        return self.fullname

    @property
    def fullname(self):
        names = [
            self.first_name,
            self.last_name,
        ]
        return u' '.join([name for name in names if name])


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
