from plone import api
from ploneintranet.workspace.tests.base import BaseTestCase
from plone.app.testing import logout

VIEW = 'View'
DELETE = 'Delete objects'


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
            self.workspace_container,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace')

        document_workspace = api.content.create(
            workspace_folder,
            'Document',
            'self.document-workspace'
        )
        self.assertEqual('ploneintranet_workflow',
                         wftool.getWorkflowsFor(document_workspace)[0].id)


class WorkspaceContentBaseTestCase(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)
        self.login_as_portal_owner()
        api.user.create(username='wsadmin', email="admin@test.com")
        api.user.create(username='wsmember', email="member@test.com")
        api.user.create(username='nonmember', email="user@test.com")
        self.workspace_folder = api.content.create(
            self.workspace_container,
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


class TestSecretWorkspaceContentWorkflow(WorkspaceContentBaseTestCase):

    def test_setup_workflow_state(self):
        self.assertEqual(api.content.get_state(self.workspace_folder),
                         'secret',
                         'workspace is in incorrect state')

    def test_draft_state(self):
        """
        draft content can only be viewed by a team manager and owner
        it can only be deleted by the team manager and owner
        """
        admin_permissions = api.user.get_permissions(
            username='wsadmin',
            obj=self.document,
        )
        self.assertTrue(admin_permissions[VIEW],
                        'Admin cannot view draft content')
        self.assertTrue(admin_permissions[DELETE],
                        'Admin cannot delete draft content')

        member_permissions = api.user.get_permissions(
            username='wsmember',
            obj=self.document,
        )
        self.assertFalse(member_permissions[VIEW],
                         'Member can view draft content')
        self.assertFalse(member_permissions[DELETE],
                         'Member can delete draft content')

        nonmember_permissions = api.user.get_permissions(
            username='nonmember',
            obj=self.document,
        )
        self.assertFalse(nonmember_permissions[VIEW],
                         'Non-member can view draft content')
        self.assertFalse(nonmember_permissions[DELETE],
                         'Non-member can delete draft content')

        logout()
        anon_permissions = api.user.get_permissions(
            obj=self.document,
        )
        self.assertFalse(anon_permissions[VIEW],
                         'Anonymous can view draft content')
        self.assertFalse(anon_permissions[DELETE],
                         'Anonymous can delete draft content')

    def test_pending_state(self):
        """
        team managers should be able to view pending items,
        team members should not
        team managers should be able to delete pending items, team members and
        owners should not
        """
        api.content.transition(self.document, 'submit')

        admin_permissions = api.user.get_permissions(
            username='wsadmin',
            obj=self.document,
        )
        self.assertTrue(admin_permissions[VIEW],
                        'Admin cannot view pending content')
        self.assertTrue(admin_permissions[DELETE],
                        'Admin cannot delete pending content')

        member_permissions = api.user.get_permissions(
            username='wsmember',
            obj=self.document,
        )
        self.assertFalse(member_permissions[VIEW],
                         'member can view pending content')
        self.assertFalse(member_permissions[DELETE],
                         'member can delete pending content')

        nonmember_permissions = api.user.get_permissions(
            username='nonmember',
            obj=self.document,
        )
        self.assertFalse(nonmember_permissions[VIEW],
                         'nonmember can view pending content')
        self.assertFalse(nonmember_permissions[DELETE],
                         'nonmember can delete pending content')

        logout()
        anon_permissions = api.user.get_permissions(
            obj=self.document,
        )
        self.assertFalse(anon_permissions[VIEW],
                         'Anonymous can view pending content')
        self.assertFalse(anon_permissions[DELETE],
                         'Anonymous can delete pending content')

    def test_published_state(self):
        """
        all team members should be able to see published content,
        regular plone user should not
        only team managers should be able to delete published content
        """
        api.content.transition(self.document, 'submit')
        api.content.transition(self.document, 'publish')

        admin_permissions = api.user.get_permissions(
            username='wsadmin',
            obj=self.document,
        )
        self.assertTrue(admin_permissions[VIEW],
                        'Admin cannot view published content')
        self.assertTrue(admin_permissions[DELETE],
                        'Admin cannot delete published content')

        member_permissions = api.user.get_permissions(
            username='wsmember',
            obj=self.document,
        )
        self.assertTrue(member_permissions[VIEW],
                        'member cannot view published content')
        self.assertFalse(member_permissions[DELETE],
                         'member can delete published content')

        nonmember_permissions = api.user.get_permissions(
            username='nonmember',
            obj=self.document,
        )
        self.assertFalse(nonmember_permissions[VIEW],
                         'user can view workspace content')
        self.assertFalse(nonmember_permissions[DELETE],
                         'user can delete workspace content')

        logout()
        anon_permissions = api.user.get_permissions(
            obj=self.document,
        )
        self.assertFalse(anon_permissions[VIEW],
                         'Anonymous can view draft content')
        self.assertFalse(anon_permissions[DELETE],
                         'Anonymous can delete draft content')


class TestPrivateWorkspaceContentWorkflow(TestSecretWorkspaceContentWorkflow):
    """
    Content in a private workspace should have the same security
    View protections as content in a secret workspace.
    Inherit the test.
    """

    def setUp(self):
        TestSecretWorkspaceContentWorkflow.setUp(self)
        api.content.transition(self.workspace_folder,
                               'make_private')

    def test_setup_workflow_state(self):
        self.assertEqual(api.content.get_state(self.workspace_folder),
                         'private',
                         'workspace is in incorrect state')


class TestOpenWorkspaceContentWorkflow(WorkspaceContentBaseTestCase):
    """
    Content in an open workspace has different View settings.
    re-implement all test methods.
    """

    def setUp(self):
        WorkspaceContentBaseTestCase.setUp(self)
        api.content.transition(self.workspace_folder,
                               'make_open')

    def test_setup_workflow_state(self):
        self.assertEqual(api.content.get_state(self.workspace_folder),
                         'open',
                         'workspace is in incorrect state')

    def test_draft_state(self):
        """
        draft content can only be viewed by a team manager and owner
        draft content can only be deleted by a team manger and owner
        """
        admin_permissions = api.user.get_permissions(
            username='wsadmin',
            obj=self.document,
        )
        self.assertTrue(admin_permissions[VIEW],
                        'Admin cannot view draft content')
        self.assertTrue(admin_permissions[DELETE],
                        'Admin cannot delete draft content')

        member_permissions = api.user.get_permissions(
            username='wsmember',
            obj=self.document,
        )
        self.assertFalse(member_permissions[VIEW],
                         'Member can view draft content')
        self.assertFalse(member_permissions[DELETE],
                         'Member can delete draft content')

        nonmember_permissions = api.user.get_permissions(
            username='nonmember',
            obj=self.document,
        )
        self.assertFalse(nonmember_permissions[VIEW],
                         'Non-member can view draft content')
        self.assertFalse(nonmember_permissions[DELETE],
                         'Non-member can delete draft content')

        logout()
        anon_permissions = api.user.get_permissions(
            obj=self.document,
        )
        self.assertFalse(anon_permissions[VIEW],
                         'Anonymous can view draft content')
        self.assertFalse(anon_permissions[DELETE],
                         'Anonymous can delete draft content')

    def test_pending_state(self):
        """
        team managers should be able to view pending items,
        team members should not
        team managers should be able to delete pending items,
        team members should not
        """
        api.content.transition(self.document, 'submit')

        admin_permissions = api.user.get_permissions(
            username='wsadmin',
            obj=self.document,
        )
        self.assertTrue(admin_permissions[VIEW],
                        'Admin cannot view pending content')
        self.assertTrue(admin_permissions[DELETE],
                        'Admin cannot delete pending content')

        member_permissions = api.user.get_permissions(
            username='wsmember',
            obj=self.document,
        )
        self.assertFalse(member_permissions[VIEW],
                         'member can view pending content')
        self.assertFalse(member_permissions[DELETE],
                         'member can delete pending content')

        nonmember_permissions = api.user.get_permissions(
            username='nonmember',
            obj=self.document,
        )
        self.assertFalse(nonmember_permissions[VIEW],
                         'nonmember can view pending content')
        self.assertFalse(nonmember_permissions[DELETE],
                         'nonmember can delete pending content')

        logout()
        anon_permissions = api.user.get_permissions(
            obj=self.document,
        )
        self.assertFalse(anon_permissions[VIEW],
                         'Anonymous can view pending content')
        self.assertFalse(anon_permissions[DELETE],
                         'Anonymous can delete pending content')

    def test_published_state(self):
        """
        all team members should be able to see published content,
        regular plone users should also
        only team managers should be able to delete published content
        """
        api.content.transition(self.document, 'submit')
        api.content.transition(self.document, 'publish')

        admin_permissions = api.user.get_permissions(
            username='wsadmin',
            obj=self.document,
        )
        self.assertTrue(admin_permissions[VIEW],
                        'Admin cannot view published content')
        self.assertTrue(admin_permissions[DELETE],
                        'Admin cannot delete published content')

        member_permissions = api.user.get_permissions(
            username='wsmember',
            obj=self.document,
        )
        self.assertTrue(member_permissions[VIEW],
                        'member cannot view published content')
        self.assertFalse(member_permissions[DELETE],
                         'member can delete published content')

        nonmember_permissions = api.user.get_permissions(
            username='nonmember',
            obj=self.document,
        )
        self.assertTrue(nonmember_permissions[VIEW],
                        'user cannot view workspace content')
        self.assertFalse(nonmember_permissions[DELETE],
                         'user can delete workspace content')

        logout()
        anon_permissions = api.user.get_permissions(
            obj=self.document,
        )
        self.assertFalse(anon_permissions[VIEW],
                         'Anonymous can view draft content')
        self.assertFalse(anon_permissions[VIEW],
                         'Anonymous can view draft content')
