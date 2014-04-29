from ploneintranet.workspace.tests.base import BaseTestCase
from plone import api
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

        # default state is private
        self.assertEqual(api.content.get_state(workspace_folder),
                         'private')

        api.user.create(username='testuser1', email="test@test.com")
        permissions = api.user.get_permissions(
            username='testuser1',
            obj=workspace_folder,
        )
        self.assertIn('View', permissions,
                      'Non-member cannot view private workspace')
        self.assertNotIn('Access contents information', permissions,
                         'Non-member can access contents of private workspace')

        IWorkspace(workspace_folder).add_to_team(
            user=api.user.get('testuser1')
        )

        member_permissions = api.user.get_permissions(
            username='testuser1',
            obj=workspace_folder,
        )
        # Normal users can view
        self.assertIn('View', member_permissions,
                      'Non-member cannot view private workspace')
        # ... and get access to
        self.assertIn('Access contents information', member_permissions,
                      'Non-member cannot access contents of private workspace')

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

        # Ssssh...
        api.content.transition(workspace_folder,
                               'make_secret')

        api.user.create(username='testuser1', email="test@test.com")
        permissions = api.user.get_permissions(
            username='testuser1',
            obj=workspace_folder,
        )
        self.assertNotIn('View', permissions,
                         'Non-member can view secret workspace')
        self.assertNotIn('Access contents information', permissions,
                         'Non-member can access contents of secret workspace')

        IWorkspace(workspace_folder).add_to_team(
            user=api.user.get('testuser1')
        )

        member_permissions = api.user.get_permissions(
            username='testuser1',
            obj=workspace_folder,
        )
        # Normal users can view
        self.assertIn('View', member_permissions,
                      'Non-member cannot view secret workspace')
        # ... and get access to
        self.assertIn('Access contents information', member_permissions,
                      'Non-member cannot access contents of secret workspace')

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

        api.user.create(username='testuser1', email="test@test.com")
        permissions = api.user.get_permissions(
            username='testuser1',
            obj=workspace_folder,
        )
        self.assertIn('View', permissions,
                      'Non-member cannot view open workspace')
        self.assertIn('Access contents information', permissions,
                      'Non-member cannot access contents of open workspace')

        IWorkspace(workspace_folder).add_to_team(
            user=api.user.get('testuser1')
        )

        member_permissions = api.user.get_permissions(
            username='testuser1',
            obj=workspace_folder,
        )
        # Normal users can view
        self.assertIn('View', member_permissions,
                      'Member cannot view open workspace')
        # ... and get access to
        self.assertIn('Access contents information', member_permissions,
                      'Member cannot access contents of open workspace')
