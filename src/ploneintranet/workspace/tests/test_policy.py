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
        self.assertEqual(workspace.external_visibility, "secret")
        self.assertEqual(workspace.join_policy, "admin")
        self.assertEqual(workspace.participant_policy, "Consumers")

        workspace.set_external_visibility("open")
        self.assertEqual(workspace.external_visibility, "open")

        workspace.join_policy = "team"
        self.assertEqual(workspace.join_policy, "team")

        workspace.participant_policy = "Producers"
        self.assertEqual(workspace.participant_policy, "Producers")

    def test_workspace_policy_change_updates_existing_members(self):
        """
        Test that changing workspace policy updates all existing members
        with a new group.
        """
        self.login_as_portal_owner()
        workspace = api.content.create(
            self.portal,
            "ploneintranet.workspace.workspacefolder",
            "example-workspace",
            title="A workspace")
        # check that accessing setting for the first time doesn't fail
        workspace.participant_policy = "Producers"
        self.assertEqual(workspace.participant_policy, "Producers")

        username = "member_username"
        api.user.create(username=username, email="test@test.com")
        self.add_user_to_workspace(username, workspace)
        group = api.group.get("Producers:" + api.content.get_uuid(workspace))
        self.assertIn(api.user.get(username=username),
                      group.getAllGroupMembers())
        workspace.participant_policy = "Consumers"
        self.assertNotIn(
            api.user.get(username=username),
            group.getAllGroupMembers())

        group = api.group.get("Consumers:" + api.content.get_uuid(workspace))
        self.assertIn(
            api.user.get(username=username),
            group.getAllGroupMembers())

    def test_members_are_correctly_added_to_group_by_policy(self):
        """
        Check that members are correctly assigned to groups
        according to workspace policy settings and have correct roles
        """
        self.login_as_portal_owner()
        workspace = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacefolder',
            'workspace')
        # default participant policy state should be "consumers"
        self.assertEqual(workspace.participant_policy, "Consumers")

        # create a member and add to workspace
        username = "member_username"
        api.user.create(username=username, email="test@test.com")
        self.add_user_to_workspace(username, workspace)

        group = api.group.get("Consumers:" + api.content.get_uuid(workspace))
        self.assertIn(api.user.get(username=username),
                      group.getAllGroupMembers())

        self.login(username)
        self.assertIn("Reader",
                      api.user.get_roles(username=username, obj=workspace))

        self.login_as_portal_owner()
        workspace = api.content.create(
            self.portal,
            "ploneintranet.workspace.workspacefolder",
            "other-workspace")
        self.assertEqual(workspace.participant_policy, "Consumers")
        workspace.participant_policy = "Producers"
        self.assertEqual(workspace.participant_policy, "Producers")
        username = "Vladislav"
        api.user.create(username=username, email="test1@test.com")
        self.add_user_to_workspace(username, workspace)
        group = api.group.get("Producers:" + api.content.get_uuid(workspace))
        self.assertIn(api.user.get(username=username),
                      group.getAllGroupMembers())
        self.login(username)
        self.assertIn("Contributor",
                      api.user.get_roles(username=username, obj=workspace))
        self.assertIn("Reader",
                      api.user.get_roles(username=username, obj=workspace))
        self.assertNotIn("Reviewer",
                         api.user.get_roles(username=username, obj=workspace))

    def test_role_adapter(self):
        """
        test that the self publishers are also given reviewers if they
        are an owner
        """
        self.login_as_portal_owner()
        # first check that the role adapter doesn't add any roles
        # if a workspace cannot be acquired
        api.user.create(
            username='mrmanager',
            email="manager@test.com",
            roles=("Member", "Manager"),
        )
        self.login('mrmanager')
        folder = api.content.create(
            self.portal,
            'Folder',
            'folder',
        )
        local_roles = api.user.get_roles(
            obj=folder,
        )
        self.assertIn('Owner', local_roles)

        self.login_as_portal_owner()
        workspace = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacefolder',
            'workspace')
        workspace.participant_policy = "Publishers"
        username = "testuser"
        api.user.create(username=username, email="test@test.com")
        self.add_user_to_workspace(username, workspace)

        self.login(username)
        doc = api.content.create(
            container=workspace,
            type='Document',
            id='my-doc',
        )
        local_roles = api.user.get_roles(
            username=username,
            obj=doc,
        )
        self.assertIn('Owner', local_roles)
        self.assertIn('Contributor', local_roles)
        self.assertIn('SelfPublisher', local_roles)
        self.assertIn('Reviewer', local_roles)
