# coding=utf-8
from ploneintranet.workspace.tests.base import BaseTestCase
from plone import api
from ploneintranet import api as pi_api


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
        msg = msgs[0]  # noqa
        self.assertTrue(msg['Subject'].startswith(u'invitees_members: 20'))
        self.assertEqual(msg['From'], 'None <None>')
        self.assertEqual(msg['To'], 'invitee <invitee@example.com>')
        text, html = msg.get_payload()
        self.assertTrue(
            text.get_payload().startswith('Dear Mr./Ms. invitee,\n')
        )
        self.assertTrue(
            html.get_payload().startswith('<p>Dear Mr./Ms. invitee,</p>\n')
        )
