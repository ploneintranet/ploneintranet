from collective.workspace.interfaces import IWorkspace
from plone import api
from ploneintranet.workspace.tests.base import BaseTestCase
from zope.annotation.interfaces import IAnnotations


class TestWorkflow(BaseTestCase):

    def test_default_workflow(self):
        """
        the ploneintranet workflow should be set as the default workflow
        """
        wftool = api.portal.get_tool('portal_workflow')
        self.assertIn('ploneintranet_workflow',
                      wftool.listWorkflows())
        self.assertIn('ploneintranet_workflow',
                      wftool.getDefaultChain())

    def test_draft_state(self):
        """
        draft content can only be viewed by a team manager and owner
        """
        self.login_as_portal_owner()
        # add non-member
        api.user.create(username='nonmember', email="test@test.com")
        api.user.create(username='wsadmin', email="admin@test.com")
        workspace_folder = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace')
        IWorkspace(workspace_folder).add_to_team(
            user='wsadmin',
            groups=set(['Admins']),
        )
        IAnnotations(self.request)[('workspaces', 'workspaceadmin')] = None
        admin_permissions = api.user.get_permissions(
            username='wsadmin',
            obj=workspace_folder,
        )
        self.assertTrue(admin_permissions['Modify portal content'],
                        'Admin cannot modify workspace')

        document = api.content.create(
            workspace_folder,
            'Document',
            'document1')

        # a non-member should not be able to view a draft item
        permissions = api.user.get_permissions(
            username='nonmember',
            obj=document,
        )
        self.assertFalse(permissions['View'],
                         'Non-member can view draft content')
