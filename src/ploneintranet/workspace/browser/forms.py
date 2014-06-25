from collective.workspace.interfaces import IWorkspace
from collective.workspace.vocabs import UsersSource
from plone import api
from plone.directives import form
from plone.formwidget.autocomplete import AutocompleteFieldWidget
from z3c.form import button
from z3c.form.interfaces import WidgetActionExecutionError
from zope import schema
from zope.component import getUtility
from zope.interface import directlyProvides, Invalid
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from ploneintranet.invitations.interfaces import ITokenUtility
from ploneintranet.workspace import MessageFactory as _
from ploneintranet.workspace.utils import get_storage, send_email


visibility_vocab = SimpleVocabulary([
    SimpleTerm(value=u'secret', title=_(u'Secret')),
    SimpleTerm(value=u'private', title=_(u'Private')),
    SimpleTerm(value=u'open', title=_(u'Open')),
    ])

join_vocab = SimpleVocabulary([
    SimpleTerm(value=u'admin', title=_(u'Admin-Managed')),
    SimpleTerm(value=u'team', title=_(u'Team-Managed')),
    SimpleTerm(value=u'self', title=_(u'Self-Managed')),
    ])

particip_vocab = SimpleVocabulary([
    SimpleTerm(value=u'consumers', title=_(u'Consumers')),
    SimpleTerm(value=u'producers', title=_(u'Producers')),
    SimpleTerm(value=u'publishers', title=_(u'Publishers')),
    SimpleTerm(value=u'moderators', title=_(u'Moderators')),
    ])


def user_has_email(username):
    """ make sure, that given user has an email associated """
    user = api.user.get(username=username)
    if not user.getProperty("email"):
        msg = "For unknown reasons, this user doesn't have an email \
associated with his account"
        raise Invalid(msg)

    return True


class IPolicyForm(form.Schema):
    """ Policy form fields, essentially radio buttons"""

    external_visibility = schema.Choice(
        title=_(u"ws_external_visibility", default="External Visibility"),
        source=visibility_vocab,
        )

    join_policy = schema.Choice(
        title=_(u"ws_join_policy", default="Join Policy"),
        source=join_vocab,
        )

    participant_policy = schema.Choice(
        title=_(u"ws_participant_policy", default="Participant Policy"),
        source=particip_vocab,
        )


class PolicyForm(form.SchemaForm):

    schema = IPolicyForm
    ignoreContext = True

    label = u"Workspace Policies"

    @button.buttonAndHandler(u'Ok')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        ws = self.context
        ws.set_external_visibility(data.get("external_visibility", "private"))
        ws.join_policy = data.get("join_policy", "admin")
        ws.participant_policy = data.get("participant_policy", "consumers")

        self.updateWidgets()
        self.status = "Policy updated."

    @button.buttonAndHandler(u"Cancel")
    def handleCancel(self, action):
        """User cancelled. Redirect back to the front page.
        """

    def updateWidgets(self):
        super(PolicyForm, self).updateWidgets()
        ws = self.context
        self.widgets["external_visibility"].value = ws.external_visibility
        self.widgets["join_policy"].value = ws.join_policy
        self.widgets["participant_policy"].value = ws.participant_policy


def workspaces_provider(context):
    catalog = api.portal.get_tool(name="portal_catalog")
    workspaces = catalog(portal_type="ploneintranet.workspace.workspacefolder")
    current = api.content.get_uuid(context)

    terms = []
    for ws in workspaces:
        if current != ws["UID"]:
            terms.append(SimpleVocabulary.createTerm(
                ws["UID"], ws["UID"], ws["Title"]))

    return SimpleVocabulary(terms)

directlyProvides(workspaces_provider, IContextSourceBinder)


class ITransferMembershipForm(form.Schema):

    workspace = schema.Choice(
        title=_(u"Select workspace"),
        source=workspaces_provider,
        )

    move = schema.Bool(
        title=_(u"Move"),
        description=_(u"If checked, users will be removed from workspace"),
        required=False,
        )


class TransferMembershipForm(form.SchemaForm):
    schema = ITransferMembershipForm
    ignoreContext = True

    label = u"Transfer membership"

    @button.buttonAndHandler(u"Ok")
    def handleApply(self, action):
        data = self.extractData()[0]

        ws = IWorkspace(self.context)
        other_ws_id = data.get("workspace")
        other_ws = IWorkspace(api.content.get(UID=other_ws_id))
        move = data.get("move", False)
        removable = []
        for member in ws.members:
            user = api.user.get(username=member)
            if user is not None:
                user_id = user.getId()
                other_ws.add_to_team(user=user_id)
            removable.append(member)

        if move:
            func = lambda member: ws.membership_factory(
                ws,
                {"user": member}).remove_from_team()
            map(func, removable)

        self.updateWidgets()
        self.status = "Members transfered."


class IInviteForm(form.Schema):

    form.widget(user=AutocompleteFieldWidget)
    user = schema.Choice(
        title=u'User',
        source=UsersSource,
        constraint=user_has_email,
        )


class InviteForm(form.SchemaForm):
    schema = IInviteForm
    ignoreContext = True

    label = u"Invitations"

    @button.buttonAndHandler(u"Ok")
    def handleApply(self, action):
        data = self.extractData()[0]
        given_username = data.get("user", "").strip()
        if not given_username:
            return

        ws = IWorkspace(self.context)
        for name in ws.members:
            member = api.user.get(username=name)
            if member is not None:
                if member.getUserName() == given_username:
                    raise WidgetActionExecutionError(
                        'user',
                        Invalid("User is already a member of this workspace"))

        user = api.user.get(username=given_username)
        email = user.getProperty("email")

        token_util = getUtility(ITokenUtility)
        token_id, token_url = token_util.generate_new_token(
            redirect_path="resolveuid/%s" % (ws.context.UID(),))
        storage = get_storage()
        storage[token_id] = (ws.context.UID(), given_username)
        message = """Congratulations! You've been invited to join %s

The following is a unique URL tied to your email address (%s).
Clicking the link will make you a member of a %s workspace automatically.

%s

Good luck,
Yours

***** Email confidentiality notice *****
This message is private and confidential. If you have received this
message in error, please notify us and UNREAD it.
""" % (self.context.title, email, self.context.title, token_url)

        subject = 'You are invited to "%s"' % self.context.title

        send_email(email, subject, message)
        api.portal.show_message(
            'Invitation sent to %s' % email,
            self.request,
        )
        return
