from zope.annotation.interfaces import IAnnotations
from ploneintranet.workspace.tests.base import BaseTestCase
from plone import api
from plone.app.testing import login
from plone.app.testing import logout
from collective.workspace.interfaces import IWorkspace


class TestWorkSpaceWorkflow(BaseTestCase):

    def test_private_workspace(self):
        """
        Private workspaces should be visible to all,
        but only accessible to members
        """
        self.login_as_portal_owner()
        workspace_folder = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace',
            title='Welcome to my workspace')

        # Private means guests can View but not access...
        api.content.transition(workspace_folder,
                               'make_private')

        # add non-member
        api.user.create(username='nonmember', email="test@test.com")
        permissions = api.user.get_permissions(
            username='nonmember',
            obj=workspace_folder,
        )
        self.assertTrue(permissions['View'],
                        'Non-member cannot view private workspace')
        self.assertFalse(permissions['Access contents information'],
                         'Non-member can access contents of private workspace')

        # add member
        api.user.create(username='workspacemember', email="test@test.com")
        IWorkspace(workspace_folder).add_to_team(
            user='workspacemember',
        )
        IAnnotations(self.request)[('workspaces', 'workspacemember')] = None
        member_permissions = api.user.get_permissions(
            username='workspacemember',
            obj=workspace_folder,
        )
        # Normal users can view
        self.assertTrue(member_permissions['View'],
                        'Member cannot view private workspace')
        # ... and get access to
        self.assertTrue(member_permissions['Access contents information'],
                        'Member cannot access contents of private workspace')

        # An anonymous user should not be able to view or access the workspace
        logout()
        anon_permissions = api.user.get_permissions(
            obj=workspace_folder,
        )
        self.assertFalse(anon_permissions['View'],
                         'Anonymous can view private workspace')
        self.assertFalse(anon_permissions['Access contents information'],
                         'Anonymous can access contents of private workspace')

    def test_secret_workspace(self):
        """
        Secret workspaces should be invisible to all but members
        """
        self.login_as_portal_owner()
        workspace_folder = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace',
            title='A secret workspace')

        # default state is secret
        self.assertEqual(api.content.get_state(workspace_folder),
                         'secret')

        api.user.create(username='nonmember', email="test@test.com")
        permissions = api.user.get_permissions(
            username='nonmember',
            obj=workspace_folder,
        )
        self.assertFalse(permissions['View'],
                         'Non-member can view secret workspace')
        self.assertFalse(permissions['Access contents information'],
                         'Non-member can access contents of secret workspace')

        api.user.create(username='workspacemember', email="test@test.com")
        IWorkspace(workspace_folder).add_to_team(
            user='workspacemember',
        )
        IAnnotations(self.request)[('workspaces', 'workspacemember')] = None
        member_permissions = api.user.get_permissions(
            username='workspacemember',
            obj=workspace_folder,
        )
        # Normal users can view
        self.assertTrue(member_permissions['View'],
                        'Member cannot view secret workspace')
        # ... and get access to
        self.assertTrue(member_permissions['Access contents information'],
                        'Member cannot access contents of secret workspace')

    def test_open_workspace(self):
        """
        Open workspaces should be visible
        and accessible to all users
        """
        self.login_as_portal_owner()
        workspace_folder = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace',
            title='A secret workspace')

        api.content.transition(workspace_folder,
                               'make_open')

        api.user.create(username='nonmember', email="test@test.com")
        permissions = api.user.get_permissions(
            username='nonmember',
            obj=workspace_folder,
        )
        self.assertTrue(permissions['View'],
                        'Non-member cannot view open workspace')
        self.assertTrue(permissions['Access contents information'],
                        'Non-member cannot access contents of open workspace')

        api.user.create(username='workspacemember', email="test@test.com")
        IWorkspace(workspace_folder).add_to_team(
            user='workspacemember',
        )

        member_permissions = api.user.get_permissions(
            username='workspacemember',
            obj=workspace_folder,
        )
        # Normal users can view
        self.assertTrue(member_permissions['View'],
                        'Member cannot view open workspace')
        # ... and get access to
        self.assertTrue(member_permissions['Access contents information'],
                        'Member cannot access contents of open workspace')

    def test_modify_workspace(self):
        """
        Only a Workspace Admin should be able to edit the workspace.
        A user with the Editor role should not be able to edit the workspace.
        """
        self.login_as_portal_owner()
        workspace_folder = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace',
            title='A workspace')

        # A Workspace Member
        api.user.create(username='workspacemember', email='test@test.com')
        IWorkspace(workspace_folder).add_to_team(
            user='workspacemember',
        )
        member_permissions = api.user.get_permissions(
            username='workspacemember',
            obj=workspace_folder,
        )
        self.assertFalse(member_permissions['Modify portal content'],
                         'Member can modify workspace')

        # A Workspace Admin
        api.user.create(username='workspaceadmin', email='test@test.com')
        IWorkspace(workspace_folder).add_to_team(
            user='workspaceadmin',
            groups=set(['Admins']),
        )
        IAnnotations(self.request)[('workspaces', 'workspaceadmin')] = None
        admin_permissions = api.user.get_permissions(
            username='workspaceadmin',
            obj=workspace_folder,
        )
        self.assertTrue(admin_permissions['Modify portal content'],
                        'Admin cannot modify workspace')

        # A workspace editor
        api.user.create(username='workspaceeditor', email='test@test.com')
        IWorkspace(workspace_folder).add_to_team(
            user='workspaceeditor',
        )
        IAnnotations(self.request)[('workspaces', 'workspaceeditor')] = None
        # Grant them the Editor role on the workspace
        api.user.grant_roles(
            username='workspaceeditor',
            obj=workspace_folder,
            roles=['Editor'],
        )

        editor_permissions = api.user.get_permissions(
            username='workspaceeditor',
            obj=workspace_folder,
        )
        self.assertFalse(editor_permissions['Modify portal content'],
                         'Editor can modify workspace')

    def test_manage_workspace(self):
        """
        A Workspace Admin should have the manage workspace permission
        """

        self.login_as_portal_owner()
        workspace_folder = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace',
            title='A workspace')

        # A normal user cannot manage the workspace
        api.user.create(username='nonmember', email='test@test.com')
        permissions = api.user.get_permissions(
            username='nonmember',
            obj=workspace_folder,
        )
        self.assertFalse(
            permissions['ploneintranet.workspace: Manage workspace'],
            'Non-Member can manage workspace'
        )

        # A workspace member cannot manage the workspace
        api.user.create(username='workspacemember', email='test@test.com')
        IWorkspace(workspace_folder).add_to_team(
            user='workspacemember',
        )
        IAnnotations(self.request)[('workspaces', 'workspacemember')] = None
        member_permissions = api.user.get_permissions(
            username='workspacemember',
            obj=workspace_folder,
        )
        self.assertFalse(
            member_permissions['ploneintranet.workspace: Manage workspace'],
            'Member can manage workspace'
        )

        # A workspace admin can manage the workspace
        api.user.create(username='workspaceadmin', email='test@test.com')
        IWorkspace(workspace_folder).add_to_team(
            user='workspaceadmin',
            groups=set(['Admins']),
        )
        IAnnotations(self.request)[('workspaces', 'workspaceadmin')] = None
        admin_permissions = api.user.get_permissions(
            username='workspaceadmin',
            obj=workspace_folder,
        )
        self.assertTrue(
            admin_permissions['ploneintranet.workspace: Manage workspace'],
            'Admin cannot manage workspace'
        )

    def test_workspace_transitions(self):
        """
        A Workspace Admin should be able to change the state of a workspace
        """

        self.login_as_portal_owner()
        workspace_folder = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace',
            title='A workspace')

        api.user.create(username='workspaceadmin', email='test@test.com')
        IWorkspace(workspace_folder).add_to_team(
            user='workspaceadmin',
            groups=set(['Admins']),
        )
        IAnnotations(self.request)[('workspaces', 'workspaceadmin')] = None

        # The Admin should have the manage workspace permission
        permissions = api.user.get_permissions(
            username='workspaceadmin',
            obj=workspace_folder,
        )
        self.assertTrue(
            permissions['ploneintranet.workspace: Manage workspace'],
            'Admin cannot manage workspace'
        )

        # The Admin should be able to transition the workspace
        # through each state
        login(self.portal, 'workspaceadmin')

        api.content.transition(workspace_folder,
                               'make_private')
        self.assertEqual(api.content.get_state(workspace_folder),
                         'private')

        api.content.transition(workspace_folder,
                               'make_open')
        self.assertEqual(api.content.get_state(workspace_folder),
                         'open')

        api.content.transition(workspace_folder,
                               'make_secret')
        self.assertEqual(api.content.get_state(workspace_folder),
                         'secret')
