# coding=utf-8
from pkg_resources import resource_filename
from plone import api
from plone.app.testing.interfaces import SITE_OWNER_NAME
from ploneintranet import api as pi_api
from ploneintranet.workspace.testing import PLONEINTRANET_WORKSPACE_INTEGRATION_TESTING  # noqa
from ploneintranet.workspace.tests.base import BaseTestCase
from slc.mailrouter.browser.views import FriendlyNameAddView


class TestMailin(BaseTestCase):
    """ Test the Mailin feature
    """
    layer = PLONEINTRANET_WORKSPACE_INTEGRATION_TESTING

    def setup_users(self):
        self.profile_allan = pi_api.userprofile.create(
            username='allan_neece',
            email='allan_neece@example.com',
            approve=True,
        )
        self.profile_allan.reindexObject()

        self.profile_alice = pi_api.userprofile.create(
            username='alice_lindstrom',
            email='alice_lindstrom@example.com',
            approve=True,
        )
        self.profile_alice.reindexObject()

        # create the portal_membership records
        pm = api.portal.get_tool('portal_memberdata')
        acl = api.portal.get_tool('acl_users')
        pm.wrapUser(acl.getUser('allan_neece')).notifyModified()
        pm.wrapUser(acl.getUser('alice_lindstrom')).notifyModified()

    def create_workspace(self):
        """ returns adapted workspace folder"""
        workspace_folder = api.content.create(
            self.workspace_container,
            'ploneintranet.workspace.workspacefolder',
            'mailin-workspace',
            title='Welcome to my workspace'
        )
        # Set the friendly name
        request = workspace_folder.REQUEST
        request.form['name'] = 'mailinworkspace'
        request.form['form.submitted'] = '1'
        FriendlyNameAddView(workspace_folder, request)()
        self.add_user_to_workspace(
            'alice_lindstrom',
            workspace_folder,
            {'Admins'},
        )
        return workspace_folder

    def setUp(self):
        """ """
        pi_api.events.disable_previews()
        super(TestMailin, self).setUp()
        self.setup_users()
        self.workspace = self.create_workspace()
        self.logout()

    def tearDown(self):
        self.login(SITE_OWNER_NAME)
        self.workspace_container.manage_delObjects('mailin-workspace')
        super(TestMailin, self).tearDown()
        pi_api.events.disable_previews()

    def inject_mail(self, mail):
        ''' Mail is the filename of one of the mail
        you can find in the mailin folder
        '''
        request = self.request.clone()
        path = resource_filename(
            'ploneintranet.workspace.tests',
            'mailin/%s' % mail,
        )
        request.stdin = open(path, 'r')
        view = api.content.get_view(
            'mailrouter-inject',
            api.portal.get(),
            request
        )
        view()

    def test_mailin_attachment(self):
        """ The email is sent by alice who exists in the portal and has write
            permissions on the target workspace. This works.
        """
        self.assertEqual(api.user.get_current().name, 'Anonymous User')

        self.inject_mail('mailin_workspace.eml')

        # The email object has been created
        mail = [
            self.workspace[key] for key in self.workspace
            if key.startswith('mail')
        ][0]
        self.assertEqual(
            mail.mail_from,
            u'Alice Lindstrom <alice_lindstrom@example.com>'
        )
        self.assertTupleEqual(
            mail.mail_to,
            (u'Mailin Workspace <mailinworkspace@intranet.com>',),
        )
        self.assertTupleEqual(
            mail.mail_cc,
            (u'foo@example.com', u'bar.example.com'),
        )
        self.assertTupleEqual(
            mail.mail_bcc,
            (),
        )

        self.assertTrue(mail.mail_body.output.startswith('<html><head><meta'))

        # with two attachments
        self.assertEqual(mail['quaive.jpg'].portal_type, 'Image')
        self.assertEqual(mail['quaive.jpg'].image.getSize(), 22758)
        self.assertEqual(mail['signature.asc'].portal_type, 'File')
        self.assertIn('BEGIN PGP SIGNATURE', mail['signature.asc'].file.data)

        self.assertEqual(mail.Creator(), 'alice_lindstrom')
        self.assertEqual(mail.getOwner().getId(), 'alice_lindstrom')
        self.assertTrue(
            api.user.has_permission('View', user=mail.getOwner(), obj=mail)
        )

        # and the original email
        mail['email.eml'].file.data.startswith('From')

        # Check the the link in the mail body have been translated
        # from "cid:content-id" to "resolveuid/attachment-uid"
        self.assertIn(
            u'src="resolveuid/%s"' % mail['quaive.jpg'].UID(),
            mail.mail_body.output
        )

        # We now check that the status updates are created for the mail
        # and the attachments (disregard the original email)
        mb = pi_api.microblog.get_microblog()
        pi_api.microblog.get_microblog()
        sus = list(mb.user_values(u'alice_lindstrom'))
        self.assertListEqual(
            [mail['signature.asc'], mail['quaive.jpg'], mail],
            [su.content_context for su in sus],
        )

    def test_invalid_sender(self):
        """ The email contains a sender address unknown to the portal. The mail
            will not be delivered.
        """
        self.inject_mail('mailin_invalid_sender.eml')
        self.assertListEqual(
            [key for key in self.workspace if key.startswith('mail')],
            []
        )

    def test_no_write_permission(self):
        """ The email is send by allan_neece, a valid sender address, but he
            has no write permission in the target folder. The email
            will not be delivered.
        """
        self.inject_mail('mailin_no_write_permission.eml')
        self.assertListEqual(
            [key for key in self.workspace if key.startswith('mail')],
            []
        )
