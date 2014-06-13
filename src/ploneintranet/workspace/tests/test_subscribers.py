from plone import api
from collective.workspace.interfaces import IWorkspace

from ploneintranet.workspace.tests.base import BaseTestCase


class TestUserDeletion(BaseTestCase):
    """ Test user deletion from site (not a workspace) """

    def setUp(self):
        super(TestUserDeletion, self).setUp()
        self.login_as_portal_owner()

        self.ws = api.content.create(
            self.portal,
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
        self.assertEqual(0, len(list(IWorkspace(self.ws).members))-1)

        # lets add one user
        self.add_user_to_workspace(username, self.ws)
        self.assertEqual(1, len(list(IWorkspace(self.ws).members))-1)

        # now lets remove a user from the site
        api.user.delete(username)

        # and this user should be gone from workspace as well
        self.assertEqual(0, len(list(IWorkspace(self.ws).members))-1)
