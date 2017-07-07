# coding=utf-8
from plone import api
from ploneintranet import api as pi_api
from ploneintranet.workspace.interfaces import IWorkspaceAppContentLayer
from ploneintranet.workspace.tests.base import BaseTestCase
from zope.interface import alsoProvides


class TestWorkSpaceWorkflow(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)
        self.login_as_portal_owner()
        self.workspace_container = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacecontainer',
            'notifications-workspace-container',
            title='Workspace container for testing email notifications'
        )
        self.workspace = api.content.create(
            self.workspace_container,
            'ploneintranet.workspace.workspacefolder',
            'notifications-workspace-container',
            title='Workspace container for testing email notifications'
        )

    def get_email_invitees_view(self, obj):
        ''' Get's the "email_invitees email"
        in the context of the Plone event obj and
        with a clean request
        '''
        return api.content.get_view(
            'email_invitees',
            obj,
            self.request.clone(),
        )

    def test_email_events(self):
        ''' This is going to tests that the mail have been sent correctly
        '''
        obj = api.content.create(
            self.workspace,
            type='Event',
            title='invitees_members',
        )
        # We have a send method which return the number of errors
        # while sending the email.
        view = self.get_email_invitees_view(obj)
        self.assertEqual(view.send(), 0)
        # It should be 0 in invitees contains invalid data.
        obj.invitees = u'i-dont-exist'
        view = self.get_email_invitees_view(obj)
        self.assertEqual(view.send(), 0)
        # It should be 1 if in invitees contains valid data
        # and we have not configured the MailHost.
        pi_api.userprofile.create(
            username=u'invitee',
            email=u'invitee@example.com'
        )
        obj.invitees = u'invitee'
        view = self.get_email_invitees_view(obj)
        self.assertEqual(view.send(), 1)
        # but we have valid messages
        msgs = list(view.iter_messages())
        self.assertEqual(len(msgs), 1)
        msg = msgs[0]
        self.assertTrue(msg['Subject'].startswith(u'invitees_members: 20'))
        self.assertEqual(msg['From'], 'None <None>')
        self.assertEqual(msg['To'], 'invitee <invitee@example.com>')
        html = msg.get_payload()[0]
        self.assertTrue(
            html.get_payload().startswith('<p>Dear Mr./Ms. invitee,</p>\n')
        )

    def test_agenda_items(self):
        event = api.content.create(
            self.workspace,
            type='Event',
            title='Test assignees',
        )
        document = api.content.create(
            self.workspace,
            type='Document',
            title='Document in Agenda',
        )
        # Test default
        self.assertEqual(event.agenda_items, [])
        event.agenda_items = [
            'Prologue',
            document.UID(),
            '1234567890abcdef1234567890abcdef',
            u'☰',
            u'Epilogue',
        ]

        # Test that the view understands when an agenda item is a UID
        request = self.request.clone()
        alsoProvides(request, IWorkspaceAppContentLayer)
        event_view = api.content.get_view('event_view', event, request)
        event_view.can_edit = True
        # Check that we do not display underesolved UIDS
        self.assertEqual(len(event.agenda_items), 5)
        self.assertEqual(len(event_view.get_agenda_items()), 4)

        for item in event_view.get_agenda_items():
            if item['brain']:
                self.assertTrue(item['read_only'])
            else:
                self.assertFalse(item['read_only'])

        event_view.request.__annotations__.pop('plone.memoize')
        event_view.can_edit = False
        for item in event_view.get_agenda_items():
            self.assertTrue(item['read_only'])
