import re

from collective.workspace.interfaces import IWorkspace
from plone import api
from plone.directives import form
from z3c.form import button
from zope import schema
from zope.component import getUtility
from zope.interface import directlyProvides
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from ploneintranet.invitations.interfaces import ITokenUtility
from ploneintranet.workspace import MessageFactory as _
from ploneintranet.workspace.utils import get_storage, send_email


visibility_vocab = SimpleVocabulary([
    SimpleTerm(value=u'open', title=_(u'Open')),
    SimpleTerm(value=u'private', title=_(u'Private')),
    SimpleTerm(value=u'secret', title=_(u'Secret'))
    ])

join_vocab = SimpleVocabulary([
    SimpleTerm(value=u'self', title=_(u'Self-Managed')),
    SimpleTerm(value=u'team', title=_(u'Team-Managed')),
    SimpleTerm(value=u'admin', title=_(u'Admin-Managed'))
    ])

particip_vocab = SimpleVocabulary([
    SimpleTerm(value=u'Moderators', title=_(u'Moderators')),
    SimpleTerm(value=u'Publishers', title=_(u'Publishers')),
    SimpleTerm(value=u'Producers', title=_(u'Producers')),
    SimpleTerm(value=u'Consumers', title=_(u'Consumers'))
    ])


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

    label = u"Whats your name"

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
    email = schema.TextLine(
        title=_(u"Enter email address"),
        required=True,
        )


class InviteForm(form.SchemaForm):
    schema = IInviteForm
    ignoreContext = True

    label = u"Invitations"

    @button.buttonAndHandler(u"Ok")
    def handleApply(self, action):
        data = self.extractData()[0]
        given_email = data.get("email", "")
        # simple regex to check if email has a @ and "." and doesn't
        # have a whitespace
        if not re.match(r"[^\s@]+@[\S]+\.[\S]+", given_email):
            api.portal.show_message(
                'Doesn\'t appear to be a valid email, try again?',
                self.request,
                type="error",
            )
            return
        ws = IWorkspace(self.context)
        for name in ws.members:
            member = api.user.get(username=name)
            if member is None:
                continue
            if member.getProperty("email") == given_email:
                api.portal.show_message(
                    "User already a member of this workspace",
                    self.request,
                    type="warn",
                )
                return

        mtool = api.portal.get_tool(name="portal_membership")
        existing_member = None
        for member in mtool.listMembers():
            if member is None:
                continue
            email = member.getProperty("email")
            if given_email == email:
                existing_member = member.getUserName()
                break
        else:
            # given email is not existing user on the site
            # so far we have no story about this, therefore
            # do nothing in this case
            api.portal.show_message(
                "This email doesn't belong to any user of this site",
                self.request,
                type="warn",
            )
            return

        token_util = getUtility(ITokenUtility)
        token_id, token_url = token_util.generate_new_token(
            redirect_path="resolveuid/%s" % (ws.context.UID(),))
        storage = get_storage()
        storage[token_id] = (ws.context.UID(), existing_member)
        message = """Congratulations! You've been invited to join %s

The following is a unique URL tied to your email address (%s).
Clicking the link will make you a member of a %s workspace automatically.

%s

Good luck,
Yours

***** Email confidentiality notice *****
This message is private and confidential. If you have received this
message in error, please notify us and UNREAD it.
""" % (self.context.title, given_email, self.context.title, token_url)

        subject = 'You are invited to "%s"' % self.context.title

        send_email(given_email, subject, message)
        api.portal.show_message(
            'Invitation sent to %s' % given_email,
            self.request,
        )
        return
