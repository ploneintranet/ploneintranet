from AccessControl import Unauthorized
from ploneintranet.workspace.browser.views import BaseFileUploadView
from ploneintranet.workspace.browser.views import FileUploadView
from ploneintranet.workspace.browser.views import JoinView
from ploneintranet.workspace.browser.views import SharingView
from ploneintranet.workspace.browser.tiles.sidebar import Sidebar
from ploneintranet.workspace.browser.tiles.sidebar import \
    SidebarSettingsAdvanced
from collective.workspace.interfaces import IWorkspace
from mock import patch
from plone import api
from ploneintranet.workspace.tests.base import BaseTestCase


class BaseViewTest(BaseTestCase):
    def setUp(self):
        super(BaseViewTest, self).setUp()
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        self.login_as_portal_owner()
        self.workspace = api.content.create(
            self.portal.workspaces,
            'ploneintranet.workspace.workspacefolder',
            'demo-workspace',
            title='Demo Workspace'
        )
        self.user = api.user.create(
            email='demo@example.org',
            username='demo',
            password='demon',
        )


class TestWorkspaceSettings(BaseViewTest):

    def test_set_attributes(self):
        self.request.method = 'POST'
        self.request.form = {'title': u'Settings Test',
                             'description': u'attr write test',
                             'calendar_visible': u'selected',
                             'email': u'tester@testorg.net'}
        self.request['HTTP_REFERER'] = 'someurl'
        self.login_as_portal_owner()
        view = Sidebar(self.workspace, self.request)
        self.assertNotEqual(self.workspace.title, u'Settings Test')
        self.assertNotEqual(self.workspace.description, u'attr write test')
        self.assertNotEqual(self.workspace.calendar_visible, True)
        self.assertNotEqual(self.workspace.email, u'tester@testorg.net')
        view()
        self.assertEqual(self.workspace.title, u'Settings Test')
        self.assertEqual(self.workspace.description, u'attr write test')
        self.assertEqual(self.workspace.calendar_visible, True)
        self.assertEqual(self.workspace.email, u'tester@testorg.net')

        self.request.form = {'email': u'tester2@testorg.net'}
        # By now, request.email is also set to the above value, need
        # to rewrite explicitly
        self.request['email'] = u'tester2@testorg.net'
        view = SidebarSettingsAdvanced(self.workspace, self.request)
        self.assertNotEqual(self.workspace.email, u'tester2@testorg.net')
        view()
        self.assertEqual(self.workspace.email, u'tester2@testorg.net')


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
        self.assertNotIn("%s [member]" % (self.user.getUserName(),), view())

    def test_acquired_roles_from_policy_settings(self):
        self.login_as_portal_owner()
        policy = "moderators"
        self.workspace.participant_policy = policy
        ws = IWorkspace(self.workspace)
        ws.add_to_team(user=self.user.getUserName())
        roles = ws.available_groups.get(policy.title())
        self.request.form = {'form.button.Search': 'Search',
                             'search_term': 'demo'}
        view = SharingView(self.workspace, self.request)
        results = view.user_search_results()

        self.assertEqual(len(results), 1)
        self.assertTrue(
            all([results[0]["roles"][role] == "acquired" for role in roles]),
            "Acquired roles were not set correctly")


class TestFileUploadView(BaseViewTest):
    def setUp(self):
        super(TestFileUploadView, self).setUp()
        self.view = FileUploadView(self.workspace, self.request)

    def test_no_file_json(self):
        self.request.environ['HTTP_ACCEPT'] = 'application/json'
        self.assertEqual(self.view(), '[]')

    def test_no_file_html(self):
        self.request.environ['HTTP_ACCEPT'] = 'text/html'
        self.assertEqual(self.view(), None)
        self.assertEqual(self.request.response.getStatus(), 302)

    def test_upload_file_json(self):
        self.request.environ['HTTP_ACCEPT'] = 'application/json'
        self.request.form = {'file': 'dummy'}
        with patch.object(BaseFileUploadView, '__call__') as mock_call:
            mock_call.return_value = '{"type": "dummy"}'
            result = self.view()
            self.assertTrue(isinstance(result, str))
            self.assertNotEqual(result, '{}')

    def test_upload_file_html(self):
        self.request.environ['HTTP_ACCEPT'] = 'text/html'
        self.request.form = {'file': 'dummy'}
        with patch.object(BaseFileUploadView, '__call__') as mock_call:
            mock_call.return_value = '{"type": "dummy"}'
            self.assertEqual(self.view(), None)
            self.assertEqual(self.request.response.getStatus(), 302)
