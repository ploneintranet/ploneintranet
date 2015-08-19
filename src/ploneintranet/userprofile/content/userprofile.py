from z3c.form import validator
from zope import schema
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import Invalid
from collective import dexteritytextindexer

from plone import api as plone_api
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Container
from plone.directives import form
from plone.namedfile.field import NamedBlobImage

from ploneintranet.core import ploneintranetCoreMessageFactory as _  # noqa


class IUserProfile(form.Schema):

    """The core user profile schema.

    Most of the plone intranet UI relies on these fields.
    """

    dexteritytextindexer.searchable('username')
    username = schema.TextLine(
        title=_(u"Username"),
        required=True
    )
    person_title = schema.TextLine(
        title=_(u"Person title"),
        required=False
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


class IUserProfileAdditional(form.Schema):

    """Default additional fields for UserProfile."""

    dexteritytextindexer.searchable('job_title')
    job_title = schema.TextLine(
        title=_(u"Job title"),
        required=False
    )
    department = schema.TextLine(
        title=_(u"Department"),
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
    address = schema.Text(
        title=_(u"Address"),
        required=False
    )
    time_zone = schema.Choice(
        title=_(u"Time Zone"),
        source=u'plone.app.vocabularies.CommonTimezones',
        required=False
    )
    primary_location = schema.Choice(
        title=_(u"Primary location"),
        source=u"ploneintranet.userprofile.locations_vocabulary",
        required=False
    )
    dexteritytextindexer.searchable('biography')
    biography = schema.Text(
        title=_(u"Biography"),
        required=False
    )


alsoProvides(IUserProfileAdditional, IFormFieldProvider)


@implementer(IUserProfile)
class UserProfile(Container):

    """UserProfile content type."""

    def Title(self):
        return self.fullname

    def Description(self):
        if getattr(self, 'job_title'):
            return self.job_title

    @property
    def fullname(self):
        names = [
            self.person_title,
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
