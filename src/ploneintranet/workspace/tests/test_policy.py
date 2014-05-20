from collective.workspace.interfaces import IWorkspace
from plone import api
from ploneintranet.workspace.tests.base import BaseTestCase
from plone.app.testing import login
from zope.annotation.interfaces import IAnnotations


class TestPolicy(BaseTestCase):

    def test_groups_created(self):
        """
        When a workspace is created it should also create a number of groups
        which correlate to the various policies on a workspace:
        - Consumer
        - Producer
        - Publisher
        - Moderator
        """
        self.login_as_portal_owner()
        workspace_folder = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacefolder',
            'workspace')
        workspace_folder_uid = api.content.get_uuid(workspace_folder)

        self.assertIsNotNone(
            api.group.get('Consumers:%s' % workspace_folder_uid))
        self.assertIsNotNone(
            api.group.get('Producers:%s' % workspace_folder_uid))
        self.assertIsNotNone(
            api.group.get('Publishers:%s' % workspace_folder_uid))
        self.assertIsNotNone(
            api.group.get('Moderators:%s' % workspace_folder_uid))

    def test_workspace_creator(self):
        """
        When a workspace is created, the creator should be added
        as a Workspace Admin
        """
        self.login_as_portal_owner()

        api.user.create(username='workspacecreator', email='test@test.com')

        # Make the creater or a Contributor on the portal
        api.user.grant_roles(
            username='workspacecreator',
            obj=self.portal,
            roles=['Contributor'],
        )

        # Login as the creator and create the workspace
        login(self.portal, 'workspacecreator')
        workspace_folder = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace',
            title='A workspace')

        IAnnotations(self.request)[('workspaces', 'workspacecreator')] = None

        # The creator should now have the Manage workspace permission
        permissions = api.user.get_permissions(
            username='workspacecreator',
            obj=workspace_folder,
        )
        self.assertTrue(
            permissions['ploneintranet.workspace: Manage workspace'],
            'Creator cannot manage workspace'
        )

    def test_workspace_policy_setting(self):
        """
        Check that we are able to set permission on a workspace
        """
        self.login_as_portal_owner()
        workspace = api.content.create(
            self.portal,
            "ploneintranet.workspace.workspacefolder",
            "example-workspace",
            title="A workspace")
        # check that accessing setting for the first time doesn't fail
        self.assertEqual(workspace.external_visibility, "private")
        self.assertEqual(workspace.join_policy, "admin")
        self.assertEqual(workspace.participant_policy, "Consumers")

        workspace.external_visibility = "secret"
        self.assertEqual(workspace.external_visibility, "secret")

        workspace.join_policy = "team"
        self.assertEqual(workspace.join_policy, "team")

        workspace.participant_policy = "Producers"
        self.assertEqual(workspace.participant_policy, "Producers")

    def test_members_are_correctly_added_to_group_by_policy(self):
        """
        Check that members are correctly assigned to groups
        according to workspace policy settings.
        """
        self.login_as_portal_owner()
        workspace = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacefolder',
            'workspace')
        # default participant policy state should be "consumers"
        self.assertEqual(workspace.participant_policy, "Consumers")

        # create a member and add to workspace
        api.user.create(username='member', email="test@test.com")
        IWorkspace(workspace).add_to_team(user="member")

        group = api.group.get("Consumers:" + api.content.get_uuid(workspace))
        self.assertIn(api.user.get(username="member"),
                      group.getAllGroupMembers())
