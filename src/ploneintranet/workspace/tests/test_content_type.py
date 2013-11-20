from ploneintranet.workspace.tests.base import BaseTestCase
from plone import api
from collective.workspace.interfaces import IWorkspace


class TestContentTypes(BaseTestCase):

    def test_add_workspace(self):
        """ check that we can create our workspace type,
            and that it provides the collective.workspace behaviour
        """
        self.login_as_portal_owner()
        workspace = api.content.create(self.portal,
                                       'ploneintranet.workspace.workspace',
                                       'example-workspace',
                                       title='Welcome to my workspace')

        ws = IWorkspace(workspace, None)
        self.assertIsNotNone(
            ws,
            'Workspace type does not provide the'
            'collective.workspace behaviour',
        )

        # does the view work?
        view = workspace.restrictedTraverse('@@view')
        html = view()
        self.assertIn(workspace.title, html,
                      'Workspace title not found on view page')
