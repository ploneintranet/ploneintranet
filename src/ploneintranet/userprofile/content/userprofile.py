from collective import dexteritytextindexer
from plone import api as plone_api
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Container
from plone.directives import form
from plone.namedfile.field import NamedBlobImage
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from z3c.form import validator
from zope import schema
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import Invalid


class Email(schema.TextLine):
    ''' An email field
    '''


class Phone(schema.TextLine):
    ''' A phone field
    '''


class GooglePlace(schema.Choice):
    ''' A field that is linked in the display view to a google place search
    '''


class IUserProfile(form.Schema):

    """The core user profile schema.

    Most of the plone intranet UI relies on these fields.
    """

    # username == context.getId() == userid
    # username should never be changed because it's used as an alias for userid
    # if you need different login names, switch on use_email_as_username
    # see changeset and docs in quaive/ploneintranet#1043
    dexteritytextindexer.searchable('username')
    username = schema.TextLine(
        title=_(u"Username"),
        required=True
    )
    dexteritytextindexer.searchable('person_title')
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
    email = Email(
        title=_(u"Email"),
        required=True
    )
    portrait = NamedBlobImage(
        title=_(u"Photo"),
        required=False
    )
    form.omitted('recent_contacts')
    recent_contacts = schema.List(
        title=_("Last Contacts"),
        required=False
    )


class IUserProfileAdditional(form.Schema):

    """Default additional fields for UserProfile."""

    dexteritytextindexer.searchable('job_title')
    job_title = schema.TextLine(
        title=_(u"Job title"),
        required=False
    )
    dexteritytextindexer.searchable('department')
    department = schema.TextLine(
        title=_(u"Department"),
        required=False
    )
    dexteritytextindexer.searchable('telephone')
    telephone = Phone(
        title=_(u"Telephone Number"),
        required=False
    )
    dexteritytextindexer.searchable('mobile')
    mobile = Phone(
        title=_(u"Mobile Number"),
        required=False
    )
    dexteritytextindexer.searchable('address')
    address = schema.Text(
        title=_(u"Address"),
        required=False
    )
    time_zone = schema.Choice(
        title=_(u"Time Zone"),
        source=u'plone.app.vocabularies.CommonTimezones',
        required=False
    )
    primary_location = GooglePlace(
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
        return getattr(self, 'job_title', None)

    @property
    def fullname(self):
        names = [
            self.person_title,
            self.first_name,
            self.last_name,
        ]
        return u' '.join([name for name in names if name])

    @property
    def initials(self):
        first_name = self.first_name or ""
        last_name = self.last_name or ""
        return first_name[:1].upper() + last_name[:2].capitalize()


class UsernameValidator(validator.SimpleFieldValidator):

    """Two users can't have the same username.

    Because of #1043 it's possible that .username != .getUserName()
    so instead we rely on .username == .getUserId() which holds true
    since we don't do use_uuid_as_userid.
    """

    def validate(self, value, force=False):
        membrane_tool = plone_api.portal.get_tool('membrane_tool')
        usernames = membrane_tool._catalog.uniqueValuesFor('exact_getUserId')
        if value in usernames:
            brains = membrane_tool.searchResults(exact_getUserId=value)
            if brains and self.context != brains[0].getObject():
                raise Invalid(_("A user with this username already exists"))

        return super(UsernameValidator, self).validate(value)


validator.WidgetValidatorDiscriminators(
    UsernameValidator,
    field=IUserProfile['username'])
