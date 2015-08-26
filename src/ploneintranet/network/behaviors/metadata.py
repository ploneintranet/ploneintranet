from AccessControl.SecurityManagement import getSecurityManager
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from plone import api
from plone.app.dexterity import MessageFactory as _
from plone.app.dexterity import PloneMessageFactory as _PMF
from plone.app.dexterity.behaviors.metadata import MetadataBase
from plone.app.dexterity.behaviors.metadata import DCFieldProperty
from plone.app.z3cform.widget import AjaxSelectFieldWidget
from plone.app.z3cform.widget import DatetimeFieldWidget
from plone.app.z3cform.widget import SelectFieldWidget
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.utils import safe_unicode
from plone.supermodel import model
from plone.uuid.interfaces import IUUID
from z3c.form.interfaces import IAddForm
from z3c.form.interfaces import IEditForm
from z3c.form.widget import ComputedWidgetAttribute
from zope import schema
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.interface import Invalid
from zope.interface import invariant
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory

from ploneintranet.network.interfaces import INetworkTool


# This is a copy/fork of plone.app.dexterity.behaviors.metadata
# so we can plug personalized tagging into the Subject field.
#
# Rationale why this requires such an invasive fork, see:
# https://community.plone.org/t/how-to-change-existing-dexterity-types-and-behaviors/219 # noqa
#
# To see the changes made do 'git diff 0b05bf4e metadata.py'

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

    # Personalized tagging callflow is as follows:
    #
    # - plone.autoform.directives.widget() instantiates a
    # - plone.autoform.widgets.ParametrizedWidget(AjaxSelectFieldWidget)
    #   which, on __call__, instantiates a
    # - plone.app.z3cform.widget.AjaxSelectFieldWidget()
    #   (and wraps that in a z3c.form.FieldWidget)
    #
    # - plone.app.z3cform.widget.AjaxSelectFieldWidget
    #   gets the vocabulary utility dottedname as defined below passed in
    #   and has a pre-defined @@getVocabulary url.
    # - plone.app.z3cform.widget.AjaxSelectFieldWidget._base_args() calls
    # - plone.app.widgets.utils.get_ajax_select_options()
    #   which, if there are already subjects set, via queryUtility gets
    # - ploneintranet.network.vocabularies.PersonalizedKeywordsVocabulary
    #   and calls it with only (context) hence no personalization
    #   which is OK for the initial form rendering, before user interaction.
    #
    #   On every keystroke into the subjects select2 field,
    # - plone.app.z3cform.widget.AjaxSelectFieldWidget calls
    #   context/@@getVocabulary?name=vocabulary.name&query=searchstring
    #   which resolves into our custom view
    # - ploneintranet.network.browser.vocabulary.PersonalizedVocabularyView
    #
    # - PersonalizedVocabularyView()() = BaseVocabularyView.__call__() ->
    # - PersonalizedVocabularyView.get_vocabulary() via queryUtility gets
    # - ploneintranet.network.vocabularies.PersonalizedKeywordsVocabulary
    #   and calls it
    # - PersonalizedKeywordsVocabulary.__call__(context, request, query)
    #   which then calculates the optimal tag set for
    #   - context (the content)
    #   - request (the user)
    #   - query (the user input keystrokes)
    #   and finally wraps the constructed tag set in a returned
    # - SimpleVocabulary([SimpleTerm(value, token, title) for tag in tags])
    #   which populates the tag suggestions presented by select2.
    #
    # All of that is the normal upstream call flow ... which took a while to
    # figure out, hence this mega comment. The customizations are minimal,
    # replacing only:
    #
    # - vocabulary factory:
    #   ploneintranet.network.vocabularies.PersonalizedKeywordsVocabulary
    #     (was: plone.app.vocabularies.catalog.KeywordsVocabulary)
    #
    # - vocabulary view:
    #   ploneintranet.network.browser.vocabulary.PersonalizedVocabularyView
    #     (was: plone.app.content.browser.vocabulary.VocabularyView)
    #
    # YMMV

    directives.widget(
        'subjects',
        AjaxSelectFieldWidget,
        vocabulary='ploneintranet.network.vocabularies.Keywords'
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
        value = tuple([safe_unicode(x) for x in value])
        self.context.subject = value
        graph = getUtility(INetworkTool)
        user = api.user.get_current()
        try:
            uuid = IUUID(self.context)
        except TypeError:
            # new factory document, not registered yet
            # we'll come back to this with an event listener
            return
        if value:
            graph.tag('content', uuid, user.id, *value)
        # else value==() -> cleaned up below
        try:
            current_tags = graph.get_tags('content', uuid, user.id)
        except KeyError:
            # no tags set yet
            return
        else:
            stale = [tag for tag in current_tags if tag not in value]
            if stale:
                graph.untag('content', uuid, user.id, *stale)

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
