from collective.workspace.vocabs import UsersSource
from collective.z3cform.chosen import ChosenMultiFieldWidget
from plone import api
from plone.directives import form
from ploneintranet.simplesharing.vocabularies import WorkflowStatesSource
from z3c.form import button
from z3c.form import field
from z3c.form.interfaces import NOT_CHANGED
from zope import schema
from zope.interface import alsoProvides
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory


@provider(IContextAwareDefaultFactory)
def share_with_default(context):
    return context.users_with_local_role('Reader')


class ISimpleSharing(form.Schema):

    visibility = schema.Choice(
        title=u"Default visibility",
        description=u"Who should see this document?",
        source=WorkflowStatesSource(),
        required=True,
    )

    share_with = schema.List(
        title=u"Additional users",
        description=u"The users with whom you'd like to share this content",
        required=False,
        defaultFactory=share_with_default,
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
    fields = field.Fields(ISimpleSharing)
    fields['share_with'].widgetFactory = ChosenMultiFieldWidget

    def updateWidgets(self):
        super(SimpleSharing, self).updateWidgets()
        self.widgets['visibility'].value = self.visibility

    @button.buttonAndHandler(u"Share")
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.visibility = data.get('visibility')
        self.share_with = data.get('share_with')

        api.portal.show_message(
            message=u"Your content has been shared.",
            request=self.context.REQUEST,
        )
        self.context.reindexObjectSecurity()
        return self.request.response.redirect(
            self.context.absolute_url())

    @property
    def visibility(self):
        """Get the workflow state for this object

        :returns: workflow state id
        :rtype: str
        """
        return api.content.get_state(obj=self.context)

    @visibility.setter
    def visibility(self, value):
        if value == NOT_CHANGED:
            return
        api.content.transition(obj=self.context, transition=value)

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
