from plone.dexterity.interfaces import IDexterityContent
from plone.directives import form
from plone import api
from plone.formwidget.autocomplete import AutocompleteMultiFieldWidget
from zope.component import adapts
from zope.interface import alsoProvides, implements
from zope import schema

from collective.workspace.vocabs import UsersSource
from plone.api.exc import InvalidParameterError
from ploneintranet.simplesharing.vocabularies import WorkflowStatesSource


class ISimpleSharing(form.Schema):

    visibility = schema.Choice(
        title=u"Visibility",
        description=u"Who should see this document?",
        source=WorkflowStatesSource(),
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
        """Get the workflow state for this object

        :returns: workflow state id
        :rtype: str
        """
        return api.content.get_state(obj=self.context)

    @visibility.setter
    def visibility(self, value):
        try:
            api.content.transition(obj=self.context, to_state=value)
        except InvalidParameterError:
            api.portal.show_message(
                u'Unable to share your %s' % self.context.portal_type,
                self.context.REQUEST,
                type='error',
            )

    @property
    def share_with(self):
        """Get the users with the local role of Reader

        :returns: userids
        :rtype: list
        """
        return self.context.users_with_local_role('Reader')

    @share_with.setter
    def share_with(self, values):
        currently_shared_with = self.share_with
        for userid in [x for x in values if x not in currently_shared_with]:
            user = api.user.get(username=userid)
            api.user.grant_roles(
                user=user,
                obj=self.context,
                roles=['Reader'],
            )
        for userid in [x for x in currently_shared_with if x not in values]:
            user = api.user.get(username=userid)
            api.user.revoke_roles(
                user=user,
                obj=self.context,
                roles=['Reader'],
            )
