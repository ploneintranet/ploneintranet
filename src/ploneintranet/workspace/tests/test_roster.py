from collective.workspace.interfaces import IHasWorkspace
from plone import api
from ploneintranet.workspace.tests.base import BaseTestCase


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
