from plone.dexterity.interfaces import IDexterityContent
from plone.directives import form
from plone import api
from plone.formwidget.autocomplete import AutocompleteMultiFieldWidget
from zope.component import adapts
from zope.interface import alsoProvides, implements
from zope import schema

from collective.workspace.vocabs import UsersSource
from plone.api.exc import InvalidParameterError
from ploneintranet.simplesharing.vocabularies import WORKFLOW_MAPPING


class ISimpleSharing(form.Schema):

    visibility = schema.Choice(
        title=u"Visibility",
        description=u"Who should see this document?",
        vocabulary='ploneintranet.simplesharing.workflow_states_vocab',
        default='private',
        required=False
    )

    form.widget(share_with=AutocompleteMultiFieldWidget)
    share_with = schema.List(
        title=u"Share with",
        description=u"The users with whom you'd like to share this content",
        required=False,
        value_type=schema.Choice(
            source=UsersSource
        )
    )
alsoProvides(ISimpleSharing, form.IFormFieldProvider)


class SimpleSharing(object):

    implements(ISimpleSharing)
    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context

    @property
    def visibility(self):
        return self._visibility

    @visibility.setter
    def visibility(self, value):
        if value == 'private':
            # Don't try and set the state to the default state
            return
        end_state = WORKFLOW_MAPPING[value]
        try:
            api.content.transition(obj=self.context, to_state=end_state)
        except InvalidParameterError:
            api.portal.show_message(u'Unable to share your %s' % self.context.portal_type,
                                    self.context.REQUEST,
                                    type='error')
        else:
            self._visibility = value

    @property
    def share_with(self):
        return self._share_with

    @share_with.setter
    def share_with(self, values):
        for userid in values:
            user = api.user.get(username=userid)
            api.user.grant_roles(user=user,
                                 obj=self.context,
                                 roles=['Reader',])
        self._share_with = values