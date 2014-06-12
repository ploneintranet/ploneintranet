from plone import api
from plone.api.exc import InvalidParameterError
from plone.directives import form
from plone.formwidget.autocomplete import AutocompleteMultiFieldWidget
from z3c.form import button
from zope.interface import alsoProvides
from zope import schema

from collective.workspace.vocabs import UsersSource

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


class SimpleSharing(form.SchemaForm):

    schema = ISimpleSharing
    ignoreContext = True

    label = u"Simple Sharing"
    description = u"Who do you want to share this with"

    def updateWidgets(self):
        super(SimpleSharing, self).updateWidgets()

        self.widgets['share_with'].value = self.share_with
        self.widgets['visibility'].value = self.visibility

    @button.buttonAndHandler(u"Share")
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.visibility = data.get('visibility')
        self.share_with = data.get('share_with')

    @property
    def visibility(self):
        """Get the workflow state for this object

        :returns: workflow state id
        :rtype: str
        """
        return api.content.get_state(obj=self.context)

    @visibility.setter
    def visibility(self, value):
        if not value:
            return
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
        if values is None:
            values = []
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
