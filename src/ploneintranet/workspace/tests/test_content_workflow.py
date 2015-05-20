from plone import api
from ploneintranet.workspace.tests.base import BaseTestCase


class TestContentWorkflow(BaseTestCase):

    def test_default_workflow(self):
        """
        the ploneintranet workflow should be listed as a workflow
        """
        wftool = api.portal.get_tool('portal_workflow')
        self.assertIn('ploneintranet_workflow',
                      wftool.listWorkflows())
        # Default workflow should be set
        self.assertTrue(wftool.getDefaultChain())

    def test_placeful_workflow(self):
        """
        The ploneintranet workflowshould be applied automatically to content
        in the workspace
        """
        self.login_as_portal_owner()
        wftool = api.portal.get_tool('portal_workflow')

        # Check that a self.document has the default workflow
        self.document = api.content.create(
            self.portal,
            'Document',
            'self.document-portal'
        )
        self.assertTrue(wftool.getWorkflowsFor(self.document))

        # A self.document in the workspace should have the workspace workflow
        workspace_folder = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace')

        document_workspace = api.content.create(
            workspace_folder,
            'Document',
            'self.document-workspace'
        )
        self.assertEqual('ploneintranet_workflow',
                         wftool.getWorkflowsFor(document_workspace)[0].id)


class TestSecretWorkspaceContentWorkflow(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)
        self.login_as_portal_owner()
        api.user.create(username='wsadmin', email="admin@test.com")
        api.user.create(username='wsmember', email="member@test.com")
        api.user.create(username='nonmember', email="user@test.com")
        self.workspace_folder = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace',
            title='Welcome to my workspace')
        self.add_user_to_workspace('wsmember', self.workspace_folder)
        self.add_user_to_workspace('wsadmin', self.workspace_folder,
                                   set(['Admins']))
        self.document = api.content.create(
            self.workspace_folder,
            'Document',
            'document1')

    def test_setup_workflow_state(self):
        self.assertEqual(api.content.get_state(self.workspace_folder),
                         'secret',
                         'workspace is in incorrect state')

    def test_draft_state(self):
        """
        draft content can only be viewed by a team manager and owner
        """
        admin_permissions = api.user.get_permissions(
            username='wsadmin',
            obj=self.document,
        )
        self.assertTrue(admin_permissions['View'],
                        'Admin cannot view draft content')

        # FIXME edit, review EVERYWHERE!

        member_permissions = api.user.get_permissions(
            username='wsmember',
            obj=self.document,
        )
        self.assertFalse(member_permissions['View'],
                         'Member can view draft content')

        nonmember_permissions = api.user.get_permissions(
            username='nonmember',
            obj=self.document,
        )
        self.assertFalse(nonmember_permissions['View'],
                         'Non-member can view draft content')

        # FIXME anon

    def test_pending_state(self):
        """
        team managers should be able to view pending items,
        team members should not
        """
        api.content.transition(self.document, 'submit')

        admin_permissions = api.user.get_permissions(
            username='wsadmin',
            obj=self.document,
        )
        self.assertTrue(admin_permissions['View'],
                        'Admin cannot view pending content')

        member_permissions = api.user.get_permissions(
            username='wsmember',
            obj=self.document,
        )
        self.assertFalse(member_permissions['View'],
                         'member can view pending content')

        nonmember_permissions = api.user.get_permissions(
            username='nonmember',
            obj=self.document,
        )
        self.assertFalse(nonmember_permissions['View'],
                         'nonmember can view pending content')

        # FIXME anon

    def test_published_state(self):
        """
        all team members should be able to see published content,
        regualar plone user should not
        """
        api.content.transition(self.document, 'submit')
        api.content.transition(self.document, 'publish')

        admin_permissions = api.user.get_permissions(
            username='wsadmin',
            obj=self.document,
        )
        self.assertTrue(admin_permissions['View'],
                        'Admin cannot view published content')

        member_permissions = api.user.get_permissions(
            username='wsmember',
            obj=self.document,
        )
        self.assertTrue(member_permissions['View'],
                        'member cannot view published content')

        nonmember_permissions = api.user.get_permissions(
            username='nonmember',
            obj=self.document,
        )
        self.assertFalse(nonmember_permissions['View'],
                         'user can view workspace content')

        # FIXME anon
