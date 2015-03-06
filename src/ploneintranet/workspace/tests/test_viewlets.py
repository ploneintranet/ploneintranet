from collective.workspace.interfaces import IWorkspace
from plone import api

from ploneintranet.workspace.browser.viewlets import JoinViewlet
from ploneintranet.workspace.tests.base import BaseTestCase


class TestSelfJoinViewlet(BaseTestCase):
    def setUp(self):
        super(TestSelfJoinViewlet, self).setUp()
        self.login_as_portal_owner()
        self.workspace = api.content.create(
            self.portal,
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
