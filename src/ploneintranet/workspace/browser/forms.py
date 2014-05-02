from plone.directives import form
from z3c.form import button
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from ploneintranet.workspace import MessageFactory as _


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
    SimpleTerm(value=u'moderators', title=_(u'Moderators')),
    SimpleTerm(value=u'publishers', title=_(u'Publishers')),
    SimpleTerm(value=u'producers', title=_(u'Producers')),
    SimpleTerm(value=u'consumers', title=_(u'Consumers'))
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
        ws.external_visibility = data.get("external_visibility", "private")
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
