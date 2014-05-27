from collective.workspace.interfaces import IHasWorkspace
from plone import api
from ploneintranet.workspace.tests.base import BaseTestCase

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
