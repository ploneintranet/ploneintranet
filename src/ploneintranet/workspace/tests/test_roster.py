from AccessControl import Unauthorized
from collective.workspace.interfaces import IHasWorkspace
from plone import api
from ploneintranet.workspace.tests.base import BaseTestCase
from ploneintranet.workspace.tests.base import FunctionalBaseTestCase
from ploneintranet.workspace.browser.roster import EditRoster
from zope.component import getMultiAdapter
from zExceptions import Forbidden
from collective.workspace.interfaces import IWorkspace


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
        api.user.create(username='wsmember', email='member@test.com')
        api.user.create(username='wsmember2', email='member2@test.com')
        workspace_folder = api.content.create(
            self.workspace_container,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace'
        )
        self.add_user_to_workspace(
            'wsmember',
            workspace_folder
        )
        self.add_user_to_workspace(
            'wsmember2',
            workspace_folder
        )

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
        api.user.create(username='wsadmin', email='admin@test.com')
        api.user.create(username='wsmember', email='member@test.com')
        api.user.create(username='wsmember2', email='member@test.com')
        workspace_folder = api.content.create(
            self.workspace_container,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace'
        )
        self.add_user_to_workspace(
            'wsadmin',
            workspace_folder,
            set(['Admins'])
        )
        self.add_user_to_workspace(
            'wsmember',
            workspace_folder
        )
        self.workspace = workspace_folder

    def test_index(self):
        view = getMultiAdapter(
            (self.workspace, self.request),
            name='edit-roster'
        )
        html = view.__call__()
        self.assertIn(
            'Roster for',
            html
        )

    def test_update_roster(self):
        er = EditRoster(self.workspace, self.request)
        # This will give forbidden - see browser test
        # for further tests of this
        self.assertRaises(
            Forbidden,
            er.update_roster,
        )

    def test_existing_users(self):
        view = getMultiAdapter(
            (self.workspace, self.request),
            name='edit-roster'
        )
        users = view.existing_users()
        wsadmin = {
            'id': 'wsadmin',
            'member': True,
            'admin': True,
            'title': 'wsadmin',
            'description': '',
            'portrait':
                'http://nohost/plone/@@avatars/wsadmin',
            'cls': 'has-no-description',
        }
        self.assertIn(
            wsadmin,
            users
        )

        wsmember = {
            'id': 'wsmember',
            'member': True,
            'admin': False,
            'title': 'wsmember',
            'description': '',
            'portrait':
                'http://nohost/plone/@@avatars/wsmember',
            'cls': 'has-no-description',
        }
        self.assertIn(
            wsmember,
            users
        )

        self.assertTrue(
            'wsmember2' not in [user['id'] for user in users]
        )

    def test_users(self):
        self.request.form['search_term'] = 'wsmember2'
        view = getMultiAdapter(
            (self.workspace, self.request),
            name='edit-roster'
        )
        results = view.users()
        self.assertTrue(len(results))
        result_ids = [x['id'] for x in results]
        self.assertIn('wsmember2', result_ids)

    def test_update_users_remove_admin(self):
        """
        Remove admin role from workspace as manager
        """
        view = getMultiAdapter(
            (self.workspace, self.request),
            name='edit-roster'
        )
        settings = [
            {
                'id': 'wsadmin',
                'member': True,
                'admin': False,
            },
            {
                'id': 'wsmember',
                'member': True,
            }
        ]

        view.update_users(settings)
        members = IWorkspace(self.workspace).members
        self.assertIn(
            'wsadmin',
            members
        )
        self.assertNotIn(
            'Admins',
            IWorkspace(self.workspace).get('wsadmin').groups,
        )

    def test_update_users_remove_member(self):
        self.login('wsadmin')
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
        members = IWorkspace(self.workspace).members
        self.assertNotIn(
            'wsmember',
            members
        )

    def test_cannot_remove_member_as_member(self):
        """
        only admins can remove members
        """
        self.workspace.join_policy = 'team'

        self.login('wsmember')
        view = getMultiAdapter(
            (self.workspace, self.request),
            name='edit-roster'
        )
        settings = [{'id': 'wsmember',
                     'member': False, }]
        self.assertRaises(
            Unauthorized,
            view.update_users,
            settings,
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
        members = IWorkspace(self.workspace).members
        self.assertIn(
            'wsmember2',
            members
        )

    def test_can_add_users_member(self):
        """
        admins can add users, and members can add users in
        self/team managed workspaces
        """
        self.workspace.join_policy = 'team'

        self.login('wsmember')
        view = api.content.get_view(
            context=self.workspace,
            request=self.request,
            name='edit-roster',
        )
        self.assertTrue(view.can_add_users())


class TestEditRosterForm(FunctionalBaseTestCase):
    def setUp(self):
        super(TestEditRosterForm, self).setUp()
        self.login_as_portal_owner()
        api.user.create(username='wsmember', email='member@test.com')
        workspace_folder = api.content.create(
            self.workspace_container,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace'
        )
        self.workspace = workspace_folder

        # Commit so the testbrowser can see the workspace
        import transaction

        transaction.commit()

    def test_edit_roster_form(self):
        self.browser_login_as_site_administrator()
        self.browser.open('%s/@@edit-roster' % self.workspace.absolute_url())
        self.browser.getControl(name='search_term').value = 'wsmember'
        self.browser.getControl(name='form.button.SearchUsers').click()
        # make sure both admin checkboxes are selected
        self.browser.getControl(
            name='entries.admin:records'
        ).value = ['1', '1']
        self.browser.getControl(name='form.button.Save').click()

        # wsmember should now be an admin
        self.assertIn(
            'Admins',
            IWorkspace(self.workspace).get('wsmember').groups
        )
