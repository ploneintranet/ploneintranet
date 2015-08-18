from AccessControl import Unauthorized
from ploneintranet.workspace.tests.base import BaseTestCase
from plone import api
from plone.app.testing import login
from plone.app.testing import logout
from ploneintranet.workspace.browser.add_content import AddContent

VIEW = 'View'
ACCESS = 'Access contents information'
MODIFY = 'Modify portal content'
MANAGE = 'ploneintranet.workspace: Manage workspace'
ADD_CONTENT = 'Add portal content'
ADD_STATUS = 'Plone Social: Add Microblog Status Update'
VIEW_STATUS = 'Plone Social: View Microblog Status Update'


class TestWorkSpaceWorkflow(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)
        self.login_as_portal_owner()
        self.open_workspaces = api.content.create(
            type="ploneintranet.workspace.workspacecontainer",
            title="Open Workspaces",
            container=self.portal,
        )
        self.restricted_workspaces = api.content.create(
            type="ploneintranet.workspace.workspacecontainer",
            title="Restricted Workspaces",
            container=self.portal,
        )
        api.content.transition(self.restricted_workspaces,
                               'restrict')

        api.user.create(username='noaddrights', email="noaddrights@test.com")
        api.user.create(username='hasaddrights', email="hasaddrights@test.com")
        api.user.grant_roles(
            username='hasaddrights',
            obj=self.restricted_workspaces,
            roles=['Contributor'],
        )
        api.user.create(username='nonmember', email="user@test.com")
        api.user.create(username='wsmember', email="member@test.com")
        api.user.create(username='wsadmin', email="admin@test.com")
        self.workspace_container = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacecontainer',
            'example-workspace-container',
            title='Welcome to my example workspace container'
        )
        self.workspace_folder = api.content.create(
            self.workspace_container,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace',
            title='Welcome to my workspace'
        )
        self.add_user_to_workspace('wsmember', self.workspace_folder)
        self.add_user_to_workspace('wsadmin', self.workspace_folder,
                                   set(['Admins']))

    def test_create_workspace(self):
        """
        Test creation of a workspace
        """
        self.assertNotIn(
            'Contributor',
            api.user.get_roles(username='noaddrights',
                               obj=self.restricted_workspaces)
        )
        self.assertIn(
            'Contributor',
            api.user.get_roles(username='hasaddrights',
                               obj=self.restricted_workspaces)
        )
        logout()
        # open system. Workspaces folder is open for authenticated
        login(self.portal, 'noaddrights')
        ac = AddContent(self.open_workspaces, self.portal.REQUEST)
        ac(portal_type='ploneintranet.workspace.workspacefolder',
           title="everybody can add")
        self.assertIn('everybody-can-add',
                      self.open_workspaces.objectIds())

        ac = AddContent(self.restricted_workspaces, self.portal.REQUEST)
        portal_type = 'ploneintranet.workspace.workspacefolder'
        self.assertRaises(Unauthorized,
                          ac,
                          portal_type=portal_type,
                          title="not anyone is permitted")

        logout()
        login(self.portal, 'hasaddrights')

        ac = AddContent(self.restricted_workspaces, self.portal.REQUEST)
        ac(portal_type='ploneintranet.workspace.workspacefolder',
           title="can add when contributor")
        self.assertIn('can-add-when-contributor',
                      self.restricted_workspaces.objectIds())

        logout()

    def test_private_workspace(self):
        """
        Private workspaces should be visible and accessible
        only to members.
        NOTE: Non-members should be able to request access. Therefore they need
        limited access to some attributes of the workspace like Title.
        This scenario is NOT tested here yet.
        """
        api.content.transition(self.workspace_folder,
                               'make_private')

        admin_permissions = api.user.get_permissions(
            username='wsadmin',
            obj=self.workspace_folder,
        )
        self.assertTrue(admin_permissions[VIEW],
                        'Admin cannot view private workspace')
        self.assertTrue(admin_permissions[ACCESS],
                        'Admin cannot access contents of private workspace')
        self.assertTrue(admin_permissions[ADD_STATUS],
                        'Admin cannot add status updates')
        self.assertTrue(admin_permissions[VIEW_STATUS],
                        'Admin cannot view status updates')

        member_permissions = api.user.get_permissions(
            username='wsmember',
            obj=self.workspace_folder,
        )
        self.assertTrue(member_permissions[VIEW],
                        'Member cannot view private workspace')
        self.assertTrue(member_permissions[ACCESS],
                        'Member cannot access contents of private workspace')
        self.assertTrue(member_permissions[ADD_STATUS],
                        'Member cannot add status updates')
        self.assertTrue(member_permissions[VIEW_STATUS],
                        'Member cannot view status updates')

        nonmember_permissions = api.user.get_permissions(
            username='nonmember',
            obj=self.workspace_folder,
        )
        self.assertFalse(nonmember_permissions[VIEW],
                         'Non-member can view private workspace')
        self.assertFalse(nonmember_permissions[ACCESS],
                         'Non-member can access private workspace')
        self.assertFalse(nonmember_permissions[ADD_STATUS],
                         'Non-member can add status updates')
        self.assertFalse(nonmember_permissions[VIEW_STATUS],
                         'Non-member can view status updates')

        logout()
        anon_permissions = api.user.get_permissions(
            obj=self.workspace_folder,
        )
        self.assertFalse(anon_permissions[VIEW],
                         'Anonymous can view private workspace')
        self.assertFalse(anon_permissions[ACCESS],
                         'Anonymous can access contents of private workspace')
        self.assertFalse(anon_permissions[ADD_STATUS],
                         'Anon can add status updates')
        self.assertFalse(anon_permissions[VIEW_STATUS],
                         'Anon can view status updates')

    def test_secret_workspace(self):
        """
        Secret workspaces should be invisible to all but members
        """
        # default state is secret
        self.assertEqual(api.content.get_state(self.workspace_folder),
                         'secret')

        admin_permissions = api.user.get_permissions(
            username='wsadmin',
            obj=self.workspace_folder,
        )
        self.assertTrue(admin_permissions[VIEW],
                        'admin cannot view secret workspace')
        self.assertTrue(admin_permissions[ACCESS],
                        'admin cannot access contents of secret workspace')
        self.assertTrue(admin_permissions[ADD_STATUS],
                        'Admin cannot add status updates')
        self.assertTrue(admin_permissions[VIEW_STATUS],
                        'Admin cannot view status updates')

        member_permissions = api.user.get_permissions(
            username='wsmember',
            obj=self.workspace_folder,
        )
        self.assertTrue(member_permissions[VIEW],
                        'Member cannot view secret workspace')
        self.assertTrue(member_permissions[ACCESS],
                        'Member cannot access contents of secret workspace')
        self.assertTrue(member_permissions[ADD_STATUS],
                        'Member cannot add status updates')
        self.assertTrue(member_permissions[VIEW_STATUS],
                        'Member cannot view status updates')

        nonmember_permissions = api.user.get_permissions(
            username='nonmember',
            obj=self.workspace_folder,
        )
        self.assertFalse(nonmember_permissions[VIEW],
                         'Non-member can view secret workspace')
        self.assertFalse(nonmember_permissions[ACCESS],
                         'Non-member can access contents of secret workspace')
        self.assertFalse(nonmember_permissions[ADD_STATUS],
                         'Non-member can add status updates')
        self.assertFalse(nonmember_permissions[VIEW_STATUS],
                         'Non-member can view status updates')

        logout()
        anon_permissions = api.user.get_permissions(
            obj=self.workspace_folder,
        )
        self.assertFalse(anon_permissions[VIEW],
                         'Anonymous can view secret workspace')
        self.assertFalse(anon_permissions[ACCESS],
                         'Anonymous can access contents of secret workspace')
        self.assertFalse(anon_permissions[ADD_STATUS],
                         'Anon can add status updates')
        self.assertFalse(anon_permissions[VIEW_STATUS],
                         'Anon can view status updates')

    def test_open_workspace(self):
        """
        Open workspaces should be visible
        and accessible to all users

        Content within open workspace is also visible
        to all users
        """
        api.content.transition(self.workspace_folder,
                               'make_open')

        admin_permissions = api.user.get_permissions(
            username='wsadmin',
            obj=self.workspace_folder,
        )
        self.assertTrue(admin_permissions[VIEW],
                        'admin cannot view open workspace')
        self.assertTrue(admin_permissions[ACCESS],
                        'admin cannot access contents of open workspace')
        self.assertTrue(admin_permissions[ADD_STATUS],
                        'Admin cannot add status updates')
        self.assertTrue(admin_permissions[VIEW_STATUS],
                        'Admin cannot view status updates')

        member_permissions = api.user.get_permissions(
            username='wsmember',
            obj=self.workspace_folder,
        )
        self.assertTrue(member_permissions[VIEW],
                        'Member cannot view open workspace')
        self.assertTrue(member_permissions[ACCESS],
                        'Member cannot access contents of open workspace')
        self.assertTrue(member_permissions[ADD_STATUS],
                        'Member cannot add status updates')
        self.assertTrue(member_permissions[VIEW_STATUS],
                        'Member cannot view status updates')

        nonmember_permissions = api.user.get_permissions(
            username='nonmember',
            obj=self.workspace_folder,
        )
        self.assertTrue(nonmember_permissions[VIEW],
                        'Non-Member cannot view open workspace')
        self.assertTrue(nonmember_permissions[ACCESS],
                        'Non-Member cannot access contents of open workspace')
        self.assertFalse(nonmember_permissions[ADD_STATUS],
                         'Non-member can add status updates')
        self.assertTrue(nonmember_permissions[VIEW_STATUS],
                        'Non-member cannot view status updates')

        logout()
        anon_permissions = api.user.get_permissions(
            obj=self.workspace_folder,
        )
        self.assertFalse(anon_permissions[VIEW],
                         'Anonymous can view open workspace')
        self.assertFalse(anon_permissions[ACCESS],
                         'Anonymous can access contents of open workspace')
        self.assertFalse(anon_permissions[ADD_STATUS],
                         'Anon can add status updates')
        self.assertFalse(anon_permissions[VIEW_STATUS],
                         'Anon can view status updates')

    def test_modify_workspace(self):
        """
        Only a Workspace Admin should be able to edit the workspace.
        A user with the Editor role should not be able
        to edit the workspace itself (only the content within a workspace)
        """

        admin_permissions = api.user.get_permissions(
            username='wsadmin',
            obj=self.workspace_folder,
        )
        self.assertTrue(admin_permissions[MODIFY],
                        'Admin cannot modify workspace')

        # A workspace editor
        api.user.create(username='wseditor', email='wseditor@test.com')
        self.add_user_to_workspace('wseditor', self.workspace_folder)
        # Grant them the Editor role on the workspace
        api.user.grant_roles(
            username='wseditor',
            obj=self.workspace_folder,
            roles=['Editor'],
        )
        editor_permissions = api.user.get_permissions(
            username='wseditor',
            obj=self.workspace_folder,
        )

        # Editor cannot edit workspace itself, only content within
        self.assertFalse(editor_permissions[MODIFY],
                         'Editor can modify workspace content')

        member_permissions = api.user.get_permissions(
            username='wsmember',
            obj=self.workspace_folder,
        )
        self.assertFalse(member_permissions[MODIFY],
                         'Member can modify workspace')

        nonmember_permissions = api.user.get_permissions(
            username='nonmember',
            obj=self.workspace_folder,
        )
        self.assertFalse(nonmember_permissions[MODIFY],
                         'Non-member can modify workspace')

        logout()
        anon_permissions = api.user.get_permissions(
            obj=self.workspace_folder,
        )
        self.assertFalse(anon_permissions[MODIFY],
                         'Anon can modify workspace')

    def test_manage_workspace(self):
        """
        A Workspace Admin should have the manage workspace permission
        """
        # A workspace admin can manage the workspace
        admin_permissions = api.user.get_permissions(
            username='wsadmin',
            obj=self.workspace_folder,
        )
        self.assertTrue(
            admin_permissions[MANAGE],
            'Admin cannot manage workspace'
        )

        # A workspace member cannot manage the workspace
        member_permissions = api.user.get_permissions(
            username='wsmember',
            obj=self.workspace_folder,
        )
        self.assertFalse(
            member_permissions[MANAGE],
            'Member can manage workspace'
        )

        # A normal user cannot manage the workspace
        nonmember_permissions = api.user.get_permissions(
            username='nonmember',
            obj=self.workspace_folder,
        )
        self.assertFalse(
            nonmember_permissions[MANAGE],
            'Non-Member can manage workspace'
        )

        logout()
        anon_permissions = api.user.get_permissions(
            obj=self.workspace_folder,
        )
        self.assertFalse(
            anon_permissions[MANAGE],
            'Anon can manage workspace'
        )

    def test_workspace_transitions(self):
        """
        A Workspace Admin should be able to change the state of a workspace
        """
        # The Admin should have the manage workspace permission
        admin_permissions = api.user.get_permissions(
            username='wsadmin',
            obj=self.workspace_folder,
        )
        self.assertTrue(
            admin_permissions[MANAGE],
            'Admin cannot manage workspace'
        )

        # The Admin should be able to transition the workspace
        # through each state
        login(self.portal, 'wsadmin')

        api.content.transition(self.workspace_folder,
                               'make_private')
        self.assertEqual(api.content.get_state(self.workspace_folder),
                         'private')

        api.content.transition(self.workspace_folder,
                               'make_open')
        self.assertEqual(api.content.get_state(self.workspace_folder),
                         'open')

        api.content.transition(self.workspace_folder,
                               'make_secret')
        self.assertEqual(api.content.get_state(self.workspace_folder),
                         'secret')

        member_permissions = api.user.get_permissions(
            username='wsmember',
            obj=self.workspace_folder,
        )
        self.assertFalse(
            member_permissions[MANAGE],
            'Member can manage workspace'
        )

        nonmember_permissions = api.user.get_permissions(
            username='nonmember',
            obj=self.workspace_folder,
        )
        self.assertFalse(
            nonmember_permissions[MANAGE],
            'Non-member can manage workspace'
        )

        logout()
        anon_permissions = api.user.get_permissions(
            obj=self.workspace_folder,
        )
        self.assertFalse(
            anon_permissions[MANAGE],
            'Anon can manage workspace'
        )


class TestWorkSpaceContainerWorkflow(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)
        self.login_as_portal_owner()
        api.user.create(username='normal_user', email="user@test.com")
        api.user.create(
            username='contributor', email="contributor@test.com",
            roles=('Member', 'Contributor'))

    def test_open_workspacecontainer(self):
        """
        Check that WorkspaceContainer is by default open: all authenticated
        members can add content
        """
        self.login_as_portal_owner()
        workspace_folder = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacecontainer',
            'open-workspaces',
            title='Open Workspaces'
        )
        self.assertIn('open-workspaces', self.portal)

        # Authenticated should have the add content permission
        authenticated_permissions = api.user.get_permissions(
            username='normal_user',
            obj=workspace_folder,
        )
        self.assertTrue(
            authenticated_permissions[ADD_CONTENT],
            "Authenticated can't add content to an open workspace container"
        )

    def test_restricted_workspacecontainer(self):
        """
        Check that a restricted WorkspaceContainer prevents authenticated from
        adding content.
        """
        self.login_as_portal_owner()
        workspace_folder = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacecontainer',
            'restricted-workspaces',
            title='Restricted Workspaces'
        )
        self.assertIn('restricted-workspaces', self.portal)
        api.content.transition(obj=workspace_folder, transition='restrict')

        # Authenticated should not have the add content permission, but should
        # be able to view
        authenticated_permissions = api.user.get_permissions(
            username='normal_user',
            obj=workspace_folder,
        )
        self.assertFalse(
            authenticated_permissions[ADD_CONTENT],
            'Authenticated can add content to a restricted workspace container'
        )
        self.assertTrue(
            authenticated_permissions[VIEW],
            "Authenticated can't view a restricted workspace container"
        )
        self.assertTrue(
            authenticated_permissions[ACCESS],
            "Authenticated can't access a restricted workspace container"
        )

        # Contributor should have the add content permission
        contributor_permissions = api.user.get_permissions(
            username='contributor',
            obj=workspace_folder,
        )
        self.assertTrue(
            contributor_permissions[ADD_CONTENT],
            "Contributor can't add content to a restricted workspace container"
        )
