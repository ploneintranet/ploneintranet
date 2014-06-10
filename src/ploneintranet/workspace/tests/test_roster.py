from collective.workspace.interfaces import IHasWorkspace
from plone import api
from ploneintranet.workspace.tests.base import BaseTestCase
from zope.component import getMultiAdapter

from ploneintranet.workspace.browser.roster import merge_search_results


class TestRoster(BaseTestCase):
    """
    tests for the roster tab/view
    """

    def test_roster_access(self):
        """
        test who can access the roster tab
        and that members can see users who are part of the workspace
        """
        self.login_as_portal_owner()
        api.user.create(username='wsmember', email="member@test.com")
        api.user.create(username='wsmember2', email="member2@test.com")
        workspace_folder = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace')
        self.add_user_to_workspace(
            'wsmember',
            workspace_folder)
        self.add_user_to_workspace(
            'wsmember2',
            workspace_folder)

        self.login('wsmember')
        self.assertTrue(IHasWorkspace.providedBy(workspace_folder))
        html = workspace_folder.restrictedTraverse('@@team-roster')()

        self.assertIn('wsmember', html)
        self.assertIn('wsmember2', html)


class TestEditRoster(BaseTestCase):
    """
    tests of the roster edit view
    """

    def setUp(self):
        super(TestEditRoster, self).setUp()
        self.login_as_portal_owner()
        api.user.create(username='wsadmin', email="admin@test.com")
        api.user.create(username='wsmember', email="member@test.com")
        api.user.create(username='wsmember2', email="member@test.com")
        workspace_folder = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace')
        self.add_user_to_workspace(
            'wsadmin',
            workspace_folder,
            set(['Admins']))
        self.add_user_to_workspace(
            'wsmember',
            workspace_folder)
        self.workspace = workspace_folder

    def test_merge_search_results(self):
        """
        Simple test to make sure search results are merging by key
        """
        search = [
            {'id': 1, 'title': 'A'},
            {'id': 1, 'title': 'B'},
            {'id': 2, 'title': 'B'}
        ]

        res = merge_search_results(search, 'id')
        self.assertEqual(
            res,
            [search[0], search[2]]
        )

        res = merge_search_results(search, 'title')
        self.assertEqual(
            res,
            [search[0], search[1]]
        )

    def test_index(self):
        view = getMultiAdapter(
            (self.workspace, self.request),
            name='edit-roster'
        )
        html = view.__call__()
        self.assertIn(
            'Edit roster for',
            html
        )

    def test_redirect(self):
        """ Form should redirect to team-roster on cancel """
        view = getMultiAdapter(
            (self.workspace, self.request),
            name='edit-roster'
        )
        self.request.form['form.button.Cancel'] = True
        view.__call__()
        self.assertEqual(
            self.request.response.status,
            302
        )
        self.assertEqual(
            self.request.response.headers['location'],
            'http://nohost/plone/example-workspace/team-roster'
        )

    def test_handle_form_postback(self):
        view = getMultiAdapter(
            (self.workspace, self.request),
            name='edit-roster'
        )
        self.assertTrue(view.handle_form())

    def test_handle_form_cancel(self):
        view = getMultiAdapter(
            (self.workspace, self.request),
            name='edit-roster'
        )
        self.request.form['form.button.Cancel'] = True
        self.assertFalse(view.handle_form())

    def test_existing_users(self):
        view = getMultiAdapter(
            (self.workspace, self.request),
            name='edit-roster'
        )
        users = view.existing_users()
        wsadmin = {
            'disabled': True,
            'id': 'wsadmin',
            'member': True,
            'title': 'wsadmin',
        }
        self.assertIn(
            wsadmin,
            users
        )

        wsmember = {
            'disabled': False,
            'id': 'wsmember',
            'member': True,
            'title': 'wsmember'
        }
        self.assertIn(
            wsmember,
            users
        )

        self.assertTrue(
            'wsmember2' not in [user['id'] for user in users]
        )

    def test_user_search_results(self):
        self.request.form['search_term'] = 'wsmember2'
        view = getMultiAdapter(
            (self.workspace, self.request),
            name='edit-roster'
        )
        results = view.user_search_results()
        self.assertTrue(len(results))
        self.assertTrue(results[0]['id'] == 'wsmember2')

    def test_user_search_results_existing(self):
        self.request.form['search_term'] = 'wsadmin'
        view = getMultiAdapter(
            (self.workspace, self.request),
            name='edit-roster'
        )
        results = view.user_search_results()
        self.assertFalse(len(results))

    def test_update_users_remove_admin(self):
        """
        It shouldn't be possible to remove an admin
        """
        view = getMultiAdapter(
            (self.workspace, self.request),
            name='edit-roster'
        )
        settings = [
            {
                'id': 'wsadmin',
                'member': False,
            },
            {
                'id': 'wsmember',
                'member': True,
            }
        ]

        view.update_users(settings)
        from collective.workspace.interfaces import IWorkspace
        members = IWorkspace(self.workspace).members
        self.assertIn(
            'wsadmin',
            members
        )

    def test_update_users_remove_member(self):
        view = getMultiAdapter(
            (self.workspace, self.request),
            name='edit-roster'
        )
        settings = [
            {
                'id': 'wsmember',
                'member': False,
            },
        ]

        view.update_users(settings)
        from collective.workspace.interfaces import IWorkspace
        members = IWorkspace(self.workspace).members
        self.assertNotIn(
            'wsmember',
            members
        )

    def test_update_users_add_member(self):
        view = getMultiAdapter(
            (self.workspace, self.request),
            name='edit-roster'
        )
        settings = [
            {
                'id': 'wsmember2',
                'member': True,
            },
        ]

        view.update_users(settings)
        from collective.workspace.interfaces import IWorkspace
        members = IWorkspace(self.workspace).members
        self.assertIn(
            'wsmember2',
            members
        )
