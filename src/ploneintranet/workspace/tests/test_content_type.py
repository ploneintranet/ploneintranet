from ploneintranet.workspace.tests.base import BaseTestCase
from plone import api
from collective.workspace.interfaces import IWorkspace


class TestContentTypes(BaseTestCase):

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

        ws = IWorkspace(workspace_folder, None)
        self.assertIsNotNone(
            ws,
            'Workspace type does not provide the'
            'collective.workspace behaviour',
        )

        # does the view work?
        view = workspace_folder.restrictedTraverse('@@view')
        html = view()
        self.assertIn(workspace_folder.title, html,
                      'Workspace title not found on view page')
