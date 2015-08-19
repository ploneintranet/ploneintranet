from ploneintranet.workspace.tests.base import BaseTestCase
from plone import api


class TestWorkSpaceState(BaseTestCase):
    def test_portal_state(self):
        """
        There should be no workspace or state on the portal root
        """
        self.login_as_portal_owner()
        view = self.portal.restrictedTraverse(
            '@@ploneintranet_workspace_state'
        )
        self.assertFalse(view.workspace())
        self.assertFalse(view.state())

    def test_no_workspace(self):
        """
        Workspace and state should be none outside of a workspace
        """
        self.login_as_portal_owner()
        folder = api.content.create(
            self.portal,
            'Folder',
            'folder1'
        )
        view = folder.restrictedTraverse(
            '@@ploneintranet_workspace_state'
        )
        self.assertFalse(view.workspace())
        self.assertFalse(view.state())

    def test_workspace_on_workspace(self):
        """
        When the context is the workspace we should get the workspace back
        """
        self.login_as_portal_owner()
        workspace_folder = api.content.create(
            self.workspace_container,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace'
        )
        view = workspace_folder.restrictedTraverse(
            '@@ploneintranet_workspace_state'
        )
        self.assertEqual(workspace_folder,
                         view.workspace())

    def test_workspace_in_workspace(self):
        """
        When inside a workspace we should get the workspace back
        """
        self.login_as_portal_owner()
        workspace_folder = api.content.create(
            self.workspace_container,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace'
        )
        folder = api.content.create(
            workspace_folder,
            'Folder',
            'folder1'
        )
        view = folder.restrictedTraverse(
            '@@ploneintranet_workspace_state'
        )
        self.assertEqual(workspace_folder,
                         view.workspace())

    def test_workspace_state(self):
        """
        The current state of the workspace should be returned
        """
        self.login_as_portal_owner()
        workspace_folder = api.content.create(
            self.workspace_container,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace'
        )
        view = workspace_folder.restrictedTraverse(
            '@@ploneintranet_workspace_state'
        )
        self.assertEqual('secret',
                         view.state())

    def test_workspace_state_after_transition(self):
        """
        """
        self.login_as_portal_owner()
        workspace_folder = api.content.create(
            self.workspace_container,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace'
        )
        api.content.transition(
            workspace_folder,
            'make_private'
        )
        view = workspace_folder.restrictedTraverse(
            '@@ploneintranet_workspace_state'
        )
        self.assertEqual('private',
                         view.state())
