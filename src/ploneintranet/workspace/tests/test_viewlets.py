from collective.workspace.interfaces import IWorkspace
from plone import api

from ploneintranet.workspace.browser.viewlets import JoinViewlet
from ploneintranet.workspace.tests.base import BaseTestCase
from ploneintranet.workspace.browser.viewlets import SharingViewlet
from ploneintranet.workspace.policies import PARTICIPANT_POLICY


class TestSelfJoinViewlet(BaseTestCase):
    def setUp(self):
        super(TestSelfJoinViewlet, self).setUp()
        self.login_as_portal_owner()
        self.workspace = api.content.create(
            self.workspace_container,
            'ploneintranet.workspace.workspacefolder',
            'demo-workspace',
            title='Demo Workspace'
        )
        self.folder = api.content.create(
            self.workspace,
            'Folder',
            'inner-one',
            title='Inner folder'
        )
        self.user = api.user.create(
            email='demo@example.org',
            username='demo',
            password='demon',
        )

    def test_viewlet_invisible_while_not_in_workspace(self):
        self.workspace.join_policy = 'self'
        self.workspace.visibility = 'open'
        viewlet = JoinViewlet(self.portal, self.request, None, None)
        self.assertFalse(viewlet.visible())

    def test_viewlet_invisible_in_other_than_self_join_policy(self):
        viewlet = JoinViewlet(self.folder, self.request, None, None)
        self.assertTrue(viewlet.in_workspace())
        self.assertFalse(viewlet.visible())

    def test_viewlet_invisible_if_user_is_member(self):
        self.workspace.join_policy = 'self'
        self.workspace.visibility = 'open'
        viewlet = JoinViewlet(self.folder, self.request, None, None)
        IWorkspace(self.workspace).add_to_team(user='demo')
        self.login('demo')
        self.assertFalse(viewlet.visible())

    def test_viewlet_visibility(self):
        viewlet = JoinViewlet(self.folder, self.request, None, None)
        self.workspace.join_policy = 'self'
        self.workspace.visibility = 'open'
        self.login('demo')
        self.assertTrue(viewlet.visible())

    def test_viewlet(self):
        viewlet = JoinViewlet(self.folder, self.request, None, None)
        url = '%s/%s' % (self.workspace.absolute_url(), 'joinme')
        self.assertEqual(viewlet.join_url(), url)


class TestSharingViewlet(BaseTestCase):
    def setUp(self):
        super(TestSharingViewlet, self).setUp()
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        self.login_as_portal_owner()
        self.workspace = api.content.create(
            self.workspace_container,
            'ploneintranet.workspace.workspacefolder',
            'demoworkspace',
            title='Demo Workspace'
        )

    def test_viewlet_message_is_correct(self):
        self.workspace.participant_policy = 'moderators'
        viewlet = SharingViewlet(self.workspace, self.request, None, None)
        self.assertEqual(
            viewlet.active_participant_policy(),
            PARTICIPANT_POLICY['moderators']['title']
        )
