from AccessControl.SecurityManagement import getSecurityManager
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from datetime import datetime
from plone.app.dexterity import MessageFactory as _
from plone.app.dexterity import PloneMessageFactory as _PMF
from plone.app.z3cform.widget import AjaxSelectFieldWidget
from plone.app.z3cform.widget import DatetimeFieldWidget
from plone.app.z3cform.widget import SelectFieldWidget
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.utils import safe_unicode
from plone.supermodel import model
from z3c.form.interfaces import IAddForm
from z3c.form.interfaces import IEditForm
from z3c.form.widget import ComputedWidgetAttribute
from zope import schema
from zope.component import adapter
from zope.component.hooks import getSite
from zope.interface import Invalid
from zope.interface import invariant
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory
from zope.schema.interfaces import ISequence
from zope.schema.interfaces import IText

# Behavior interfaces to display Dublin Core metadata fields on Dexterity
# content edit forms.
#
# These schemata duplicate the fields of zope.dublincore.IZopeDublinCore,
# in order to annotate them with form hints and more helpful titles
# and descriptions.


@provider(IContextAwareDefaultFactory)
def default_language(context):
    # If we are adding a new object, context will be the folderish object where
    # this new content is being added
    language = None

    if context is not None and not IPloneSiteRoot.providedBy(context):
        language = context.Language()
        if not language:
            # If we are here, it means we were editing an object that didn't
            # have its language set or that the container where we were adding
            # the new content didn't have a language set. So we check its
            # parent, unless we are at site's root, in which case we get site's
            # default language
            if not IPloneSiteRoot.providedBy(context.aq_parent):
                language = context.aq_parent.Language()

    if not language:
        # Finally, if we still don't have a language, then just use site's
        # default
        pl = getToolByName(getSite(), 'portal_languages')
        language = pl.getDefaultLanguage()

    return language


@provider(IFormFieldProvider)
class IBasic(model.Schema):

    # default fieldset
    title = schema.TextLine(
        title=_PMF(u'label_title', default=u'Title'),
        required=True
    )

    description = schema.Text(
        title=_PMF(u'label_description', default=u'Summary'),
        description=_PMF(
            u'help_description',
            default=u'Used in item listings and search results.'
        ),
        required=False,
        missing_value=u'',
    )

    directives.order_before(description='*')
    directives.order_before(title='*')

    directives.omitted('title', 'description')
    directives.no_omit(IEditForm, 'title', 'description')
    directives.no_omit(IAddForm, 'title', 'description')


@provider(IFormFieldProvider)
class ICategorization(model.Schema):

    # categorization fieldset
    model.fieldset(
        'categorization',
        label=_PMF(u'label_schema_categorization', default=u'Categorization'),
        fields=['subjects', 'language'],
    )

    subjects = schema.Tuple(
        title=_PMF(u'label_tags', default=u'Tags'),
        description=_PMF(
            u'help_tags',
            default=u'Tags are commonly used for ad-hoc organization of ' +
                    u'content.'
        ),
        value_type=schema.TextLine(),
        required=False,
        missing_value=(),
    )
    directives.widget(
        'subjects',
        AjaxSelectFieldWidget,
        vocabulary='plone.app.vocabularies.Keywords'
    )

    language = schema.Choice(
        title=_PMF(u'label_language', default=u'Language'),
        vocabulary='plone.app.vocabularies.AvailableContentLanguages',
        required=False,
        missing_value='',
        defaultFactory=default_language,
    )
    directives.widget('language', SelectFieldWidget)

    directives.omitted('subjects', 'language')
    directives.no_omit(IEditForm, 'subjects', 'language')
    directives.no_omit(IAddForm, 'subjects', 'language')


class EffectiveAfterExpires(Invalid):
    __doc__ = _("error_invalid_publication",
                default=u"Invalid effective or expires date")


@provider(IFormFieldProvider)
class IPublication(model.Schema):
    # dates fieldset
    model.fieldset(
        'dates',
        label=_PMF(u'label_schema_dates', default=u'Dates'),
        fields=['effective', 'expires'],
    )

    effective = schema.Datetime(
        title=_PMF(u'label_effective_date', u'Publishing Date'),
        description=_PMF(
            u'help_effective_date',
            default=u"If this date is in the future, the content will "
                    u"not show up in listings and searches until this date."),
        required=False
    )
    directives.widget('effective', DatetimeFieldWidget)

    expires = schema.Datetime(
        title=_PMF(u'label_expiration_date', u'Expiration Date'),
        description=_PMF(
            u'help_expiration_date',
            default=u"When this date is reached, the content will no"
                    u"longer be visible in listings and searches."),
        required=False
    )
    directives.widget('expires', DatetimeFieldWidget)

    @invariant
    def validate_start_end(data):
        if data.effective and data.expires and data.effective > data.expires:
            raise EffectiveAfterExpires(
                _("error_expiration_must_be_after_effective_date",
                  default=u"Expiration date must be after publishing date.")
            )

    directives.omitted('effective', 'expires')
    directives.no_omit(IEditForm, 'effective', 'expires')
    directives.no_omit(IAddForm, 'effective', 'expires')


@provider(IFormFieldProvider)
class IOwnership(model.Schema):

    # ownership fieldset
    model.fieldset(
        'ownership',
        label=_PMF(
            'label_schema_ownership',
            default=u'Ownership'
        ),
        fields=['creators', 'contributors', 'rights'],
    )

    creators = schema.Tuple(
        title=_PMF(u'label_creators', u'Creators'),
        description=_PMF(
            u'help_creators',
            default=u"Persons responsible for creating the content of "
                    u"this item. Please enter a list of user names, one "
                    u"per line. The principal creator should come first."
        ),
        value_type=schema.TextLine(),
        required=False,
        missing_value=(),
    )
    directives.widget(
        'creators',
        AjaxSelectFieldWidget,
        vocabulary='plone.app.vocabularies.Users'
    )

    contributors = schema.Tuple(
        title=_PMF(u'label_contributors', u'Contributors'),
        description=_PMF(
            u'help_contributors',
            default=u"The names of people that have contributed "
                    u"to this item. Each contributor should "
                    u"be on a separate line."),
        value_type=schema.TextLine(),
        required=False,
        missing_value=(),
    )
    directives.widget(
        'contributors',
        AjaxSelectFieldWidget,
        vocabulary='plone.app.vocabularies.Users'
    )

    rights = schema.Text(
        title=_PMF(u'label_copyrights', default=u'Rights'),
        description=_PMF(
            u'help_copyrights',
            default=u'Copyright statement or other rights information on this '
                    u'item.'
        ),
        required=False,
    )

    directives.omitted('creators', 'contributors', 'rights')
    directives.no_omit(IEditForm, 'creators', 'contributors', 'rights')
    directives.no_omit(IAddForm, 'creators', 'contributors', 'rights')


# make sure the add form shows the default creator
def creatorsDefault(data):
    user = getSecurityManager().getUser()
    # NB: CMF users are UTF-8 encoded bytes, decode them before inserting
    return user and (safe_unicode(user.getId()),)

CreatorsDefaultValue = ComputedWidgetAttribute(
    creatorsDefault,
    field=IOwnership['creators']
)


@provider(IFormFieldProvider)
class IDublinCore(IOwnership, IPublication, ICategorization, IBasic):
    """ Metadata behavior providing all the DC fields
    """
    pass


@adapter(IDexterityContent)
class MetadataBase(object):
    """ This adapter uses DCFieldProperty to store metadata directly on an
        object using the standard CMF DefaultDublinCoreImpl getters and
        setters.
    """

    def __init__(self, context):
        self.context = context


_marker = object()


class DCFieldProperty(object):
    """Computed attributes based on schema fields.
    Based on zope.schema.fieldproperty.FieldProperty.
    """

    def __init__(self, field, get_name=None, set_name=None):
        if get_name is None:
            get_name = field.__name__
        self._field = field
        self._get_name = get_name
        self._set_name = set_name

    def __get__(self, inst, klass):
        if inst is None:
            return self

        attribute = getattr(inst.context, self._get_name, _marker)
        if attribute is _marker:
            field = self._field.bind(inst)
            attribute = getattr(field, 'default', _marker)
            if attribute is _marker:
                raise AttributeError(self._field.__name__)
        elif callable(attribute):
            attribute = attribute()

        if isinstance(attribute, DateTime):
            # Ensure datetime value is stripped of any timezone and seconds
            # so that it can be compared with the value returned by the widget
            return datetime(*map(int, attribute.parts()[:6]))

        if attribute is None:
            return

        if IText.providedBy(self._field):
            return attribute.decode('utf-8')

        if ISequence.providedBy(self._field):
            if IText.providedBy(self._field.value_type):
                return type(attribute)(
                    item.decode('utf-8') for item in attribute
                )

        return attribute

    def __set__(self, inst, value):
        field = self._field.bind(inst)
        field.validate(value)
        if field.readonly:
            raise ValueError(self._field.__name__, 'field is readonly')
        if isinstance(value, datetime):
            # The ensures that the converted DateTime value is in the
            # server's local timezone rather than GMT.
            value = DateTime(value.year, value.month, value.day,
                             value.hour, value.minute)
        elif value is not None:
            if IText.providedBy(self._field):
                value = value.encode('utf-8')

            elif ISequence.providedBy(self._field):
                if IText.providedBy(self._field.value_type):
                    value = type(value)(
                        item.encode('utf-8') for item in value
                    )

        if self._set_name:
            getattr(inst.context, self._set_name)(value)
        elif inst.context.hasProperty(self._get_name):
            inst.context._updateProperty(self._get_name, value)
        else:
            setattr(inst.context, self._get_name, value)

    def __getattr__(self, name):
        return getattr(self._field, name)


class Basic(MetadataBase):

    def _get_title(self):
        return self.context.title

    def _set_title(self, value):
        if isinstance(value, str):
            raise ValueError('Title must be unicode.')
        self.context.title = value
    title = property(_get_title, _set_title)

    def _get_description(self):
        return self.context.description

    def _set_description(self, value):
        if isinstance(value, str):
            raise ValueError('Description must be unicode.')

        # If description is containing linefeeds the HTML
        # validation can break.
        # See http://bo.geekworld.dk/diazo-bug-on-html5-validation-errors/

        if '\n' in value:
            value = value.replace('\n', '')

        if '\r' in value:
            value = value.replace('\r', '')

        self.context.description = value

    description = property(_get_description, _set_description)


class Categorization(MetadataBase):

    def _get_subjects(self):
        return self.context.subject

    def _set_subjects(self, value):
        self.context.subject = value
    subjects = property(_get_subjects, _set_subjects)

    language = DCFieldProperty(
        ICategorization['language'],
        get_name='Language',
        set_name='setLanguage'
    )


class Publication(MetadataBase):
    effective = DCFieldProperty(
        IPublication['effective'],
        get_name='effective_date'
    )
    expires = DCFieldProperty(
        IPublication['expires'],
        get_name='expiration_date'
    )


class Ownership(MetadataBase):
    creators = DCFieldProperty(
        IOwnership['creators'],
        get_name='listCreators',
        set_name='setCreators'
    )
    contributors = DCFieldProperty(
        IOwnership['contributors'],
        get_name='Contributors',
        set_name='setContributors'
    )
    rights = DCFieldProperty(
        IOwnership['rights'],
        get_name='Rights',
        set_name='setRights'
    )

    def __init__(self, *args, **kwargs):
        super(Ownership, self).__init__(*args, **kwargs)
        self.context.addCreator()


class DublinCore(Basic, Categorization, Publication, Ownership):
    pass
