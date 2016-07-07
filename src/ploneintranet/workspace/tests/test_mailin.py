# coding=utf-8
import os.path
from plone import api
from plone.app.testing.interfaces import SITE_OWNER_NAME
from ploneintranet.workspace.tests.base import BaseTestCase
from ploneintranet.workspace.testing import \
    PLONEINTRANET_WORKSPACE_INTEGRATION_TESTING
from slc.mailrouter.browser.views import InjectionView
from slc.mailrouter.browser.views import FriendlyNameAddView
from ploneintranet import api as pi_api


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
        super(TestMailin, self).setUp()
        self.setup_users()
        self.workspace = self.create_workspace()

    def tearDown(self):
        self.login(SITE_OWNER_NAME)
        self.workspace_container.manage_delObjects('mailin-workspace')
        super(TestMailin, self).tearDown()

    def test_mailin_attachment(self):
        """ The email is sent by alice who exists in the portal and has write
            permissions on the target workspace. This works.
        """
        self.login(SITE_OWNER_NAME)
        self.assertNotIn('quaive.jpg', self.workspace.objectIds())

        self.email_path = os.path.join(os.path.dirname(__file__),
                                       "mailin/mailin_workspace.eml")
        self.request = self.workspace.REQUEST
        self.request.stdin = open(self.email_path, 'r')
        inject = InjectionView(self.workspace, self.request)
        inject()
        self.assertIn('quaive.jpg', self.workspace.objectIds())

    def test_invalid_sender(self):
        """ The email contains a sender address unknown to the portal. The mail
            will not be delivered.
        """
        self.login(SITE_OWNER_NAME)
        self.assertNotIn('quaive.jpg', self.workspace.objectIds())

        self.email_path = os.path.join(os.path.dirname(__file__),
                                       "mailin/mailin_invalid_sender.eml")
        self.request = self.workspace.REQUEST
        self.request.stdin = open(self.email_path, 'r')
        inject = InjectionView(self.workspace, self.request)
        inject()
        self.assertNotIn('quaive.jpg', self.workspace.objectIds())

    def test_no_write_permission(self):
        """ The email is send by allan_neece, a valid sender address, but he
            has no write permission in the target folder. The email
            will not be delivered.
        """
        self.login(SITE_OWNER_NAME)
        self.assertNotIn('quaive.jpg', self.workspace.objectIds())

        self.email_path = os.path.join(os.path.dirname(__file__),
                                       "mailin/mailin_no_write_permission.eml")
        self.request = self.workspace.REQUEST
        self.request.stdin = open(self.email_path, 'r')
        inject = InjectionView(self.workspace, self.request)
        inject()
        self.assertNotIn('quaive.jpg', self.workspace.objectIds())
