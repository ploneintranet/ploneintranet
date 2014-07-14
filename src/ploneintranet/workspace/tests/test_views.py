from AccessControl import Unauthorized
from ploneintranet.workspace.browser.views import JoinView, SharingView
from collective.workspace.interfaces import IWorkspace
from plone import api
from ploneintranet.workspace.tests.base import BaseTestCase


class BaseViewTest(BaseTestCase):
    def setUp(self):
        super(BaseViewTest, self).setUp()
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        self.login_as_portal_owner()
        self.workspace = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacefolder',
            'demo-workspace',
            title='Demo Workspace'
        )
        self.user = api.user.create(
            email='demo@example.org',
            username='demo',
            password='demon',
        )


class TestSelfJoin(BaseViewTest):
    def open_workspace(self):
        self.workspace.join_policy = 'self'
        self.workspace.visibility = 'open'

    def test_user_can_join(self):
        self.open_workspace()
        self.request.method = 'POST'
        self.request.form = {'button.join': True}
        self.request['HTTP_REFERER'] = 'someurl'
        self.login('demo')
        view = JoinView(self.workspace, self.request)
        response = view()
        self.assertEqual('someurl', response)
        self.assertIn('demo', IWorkspace(self.workspace).members)

    def test_user_cant_join_if_policy_is_not_self(self):
        self.login('demo')
        view = JoinView(self.workspace, self.request)
        self.assertRaises(Unauthorized, view)

    def test_user_redirected_if_method_get(self):
        self.open_workspace()
        self.request.method = 'GET'
        self.request.form = {'button.join': True}
        self.request['HTTP_REFERER'] = 'someurl'
        self.login('demo')
        view = JoinView(self.workspace, self.request)
        response = view()
        self.assertEqual('someurl', response)
        self.assertNotIn('demo', IWorkspace(self.workspace).members)

    def test_user_redirected_to_workspace_if_no_referer(self):
        self.open_workspace()
        self.login('demo')
        view = JoinView(self.workspace, self.request)
        response = view()
        self.assertEqual(self.workspace.absolute_url(), response)


class TestSharingView(BaseViewTest):
    def test_inherit_view_is_not_shown(self):
        self.login_as_portal_owner()
        view = SharingView(self.workspace, self.request)
        self.assertFalse(view.can_edit_inherit())

    def test_sharing_view_filters_groups(self):
        self.login_as_portal_owner()
        view = SharingView(self.workspace, self.request)
        ids = [group['id'] for group in view.role_settings()]
        self.assertNotIn('AuthenticatedUsers', ids)
        uid = self.workspace.UID()
        self.assertEqual(filter(lambda x: x.endswith(uid), ids), [])

    def test_member_is_added_to_user_title_if_user_is_a_member(self):
        self.login_as_portal_owner()
        IWorkspace(self.workspace).add_to_team(user=self.user.getUserName())
        self.request.form = {'form.button.Search': 'Search',
                             'search_term': 'demo'}
        view = SharingView(self.workspace, self.request)
        self.assertIn('%s [member]' % (self.user.getUserName(),), view())

    def test_member_is_not_added_if_user_is_not_a_member(self):
        self.login_as_portal_owner()
        self.request.form = {'form.button.Search': 'Search',
                             'search_term': 'demo'}
        view = SharingView(self.workspace, self.request)
        self.assertNotIn('%s [member]' % (self.user.getUserName(),), view())

    def test_administrator_is_added_to_administrator(self):
        """ Test that [administrator] is added to the workspace
        administrator """
        self.login_as_portal_owner()
        IWorkspace(self.workspace).add_to_team(
            user=self.user.getUserName(),
            groups=set(["Admins"]))
        self.request.form = {'form.button.Search': 'Search',
                             'search_term': 'demo'}
        view = SharingView(self.workspace, self.request)
        self.assertIn(
            '%s [administrator]' % (self.user.getUserName(),),
            view())
        self.assertNotIn('%s [member]' % (self.user.getUserName(),), view())
