from ploneintranet.workspace.tests.base import BaseTestCase
from ploneintranet.workspace.config import INTRANET_USERS_GROUP_ID
from plone import api
from collective.workspace.interfaces import IWorkspace


class TestSubscribers(BaseTestCase):

    def test_workspace_state_changed(self):
        self.login_as_portal_owner()
        workspace_folder = api.content.create(
            self.workspace_container,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace')
        roles = api.group.get_roles(
            groupname=INTRANET_USERS_GROUP_ID,
            obj=workspace_folder,
        )
        self.assertNotIn('Guest', roles)

        # Transition to open should add the role
        api.content.transition(obj=workspace_folder,
                               to_state='open')
        roles = api.group.get_roles(
            groupname=INTRANET_USERS_GROUP_ID,
            obj=workspace_folder,
        )
        self.assertIn('Guest', roles)

        # Transition to another state should remove it
        api.content.transition(obj=workspace_folder,
                               to_state='private')
        roles = api.group.get_roles(
            groupname=INTRANET_USERS_GROUP_ID,
            obj=workspace_folder,
        )
        self.assertNotIn('Guest', roles)


class TestUserDeletion(BaseTestCase):
    """ Test user deletion from site (not a workspace) """

    def setUp(self):
        super(TestUserDeletion, self).setUp()
        self.login_as_portal_owner()

        self.ws = api.content.create(
            self.workspace_container,
            "ploneintranet.workspace.workspacefolder",
            "alejandro-workspace",
            title="Alejandro workspace")

    def test_user_deletion_from_site_removes_from_workspace(self):
        username = "johnsmith"
        api.user.create(
            email="user@example.org",
            username=username,
            password="doesntmatter",
        )

        # there shouldn't be any minus admin user in workspace
        self.assertEqual(0, len(list(IWorkspace(self.ws).members)) - 1)

        # lets add one user
        self.add_user_to_workspace(username, self.ws)
        self.assertEqual(1, len(list(IWorkspace(self.ws).members)) - 1)

        # now lets remove a user from the site
        api.user.delete(username)

        # and this user should be gone from workspace as well
        self.assertEqual(0, len(list(IWorkspace(self.ws).members)) - 1)
