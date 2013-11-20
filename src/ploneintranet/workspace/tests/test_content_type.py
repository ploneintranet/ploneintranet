from ploneintranet.workspace.tests.base import BaseTestCase
from plone import api
from collective.workspace.interfaces import IWorkspace


class TestContentTypes(BaseTestCase):

    def test_add_workspace(self):
        self.login_as_portal_owner()
        workspace = api.content.create(self.portal,
                                       'ploneintranet.workspace.workspace',
                                       'example-workspace')

        ws = IWorkspace(workspace, None)
        self.assertIsNotNone(
            ws,
            'Workspace type does not provide the'
            'collective.workspace behaviour',
        )
