from ploneintranet.workspace.tests.base import BaseTestCase
from plone import api
from collective.workspace.interfaces import IHasWorkspace, IWorkspace


class TestContentTypes(BaseTestCase):

    def create_workspace(self):
        workspace_folder = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace',
            title='Welcome to my workspace')
        return IWorkspace(workspace_folder)

    def test_add_workspacefolder(self):
        """ check that we can create our workspace folder type,
            and that it provides the collective.workspace behaviour
        """
        self.login_as_portal_owner()
        workspace_folder = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace',
            title='Welcome to my workspace')

        self.assertTrue(
            IHasWorkspace.providedBy(workspace_folder),
            'Workspace type does not provide the'
            'collective.workspace behaviour',
        )

        # does the view work?
        view = workspace_folder.restrictedTraverse('@@view')
        html = view()
        self.assertIn(workspace_folder.title, html,
                      'Workspace title not found on view page')

    def test_add_user_to_workspace(self):
        """ check that we can add a new user to a workspace """
        self.login_as_portal_owner()
        ws = self.create_workspace()
        user = api.user.create(
            email="test@user.com",
            username="testuser",
            password="secret",
            )
        ws.add_to_team(user=user)
        self.assertEqual(len(ws.members), 1)
        self.assertEqual(list(ws.members)[0].getUserName(), 'testuser')
