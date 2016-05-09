from plone import api
from ploneintranet.workspace.tests.base import BaseTestCase
from plone.app.testing import login
from plone.app.testing import logout

VIEW = 'View'
DELETE = 'Delete objects'
MODIFY = 'Modify portal content'


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
        # allow non-admin to create content
        self.workspace_folder.participant_policy = 'producers'
        login(self.portal, 'wsmember')
        # wsmember is owner of document2
        self.document2 = api.content.create(
            self.workspace_folder,
            'Document',
            'document2')
        self.login_as_portal_owner()


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

        owner_permissions = api.user.get_permissions(
            username='wsmember',
            obj=self.document2,
        )
        self.assertTrue(owner_permissions[VIEW],
                        'Owner cannot view draft content')
        self.assertTrue(owner_permissions[DELETE],
                        'Owner cannot delete draft content')

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
        api.content.transition(self.document2, 'submit')

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

        owner_permissions = api.user.get_permissions(
            username='wsmember',
            obj=self.document2,
        )
        self.assertTrue(owner_permissions[VIEW],
                        'Owner cannot view pending content')
        self.assertFalse(owner_permissions[DELETE],
                         'Owner should retract, not delete pending content')

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
        it can only be deleted by the team manager and owner
        """
        api.content.transition(self.document, 'submit')
        api.content.transition(self.document, 'publish')
        api.content.transition(self.document2, 'submit')
        api.content.transition(self.document2, 'publish')

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

        owner_permissions = api.user.get_permissions(
            username='wsmember',
            obj=self.document2,
        )
        self.assertTrue(owner_permissions[VIEW],
                        'Owner cannot view published content')
        self.assertFalse(owner_permissions[DELETE],
                         'Owner should retract, not delete published content')

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

        owner_permissions = api.user.get_permissions(
            username='wsmember',
            obj=self.document2,
        )
        self.assertTrue(owner_permissions[VIEW],
                        'Owner cannot view draft content')
        self.assertTrue(owner_permissions[DELETE],
                        'Owner cannot delete draft content')

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
        team managers and owners should be able to view pending items,
        team members should not
        team managers and owners should be able to delete pending items,
        team members should not
        """
        api.content.transition(self.document, 'submit')
        api.content.transition(self.document2, 'submit')

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

        owner_permissions = api.user.get_permissions(
            username='wsmember',
            obj=self.document2,
        )
        self.assertTrue(owner_permissions[VIEW],
                        'Owner cannot view pending content')
        self.assertFalse(owner_permissions[DELETE],
                         'Owner should retract, not delete pending content')

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
        team managers and owners should be able to delete published content
        """
        api.content.transition(self.document, 'submit')
        api.content.transition(self.document, 'publish')
        api.content.transition(self.document2, 'submit')
        api.content.transition(self.document2, 'publish')

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

        owner_permissions = api.user.get_permissions(
            username='wsmember',
            obj=self.document2,
        )
        self.assertTrue(owner_permissions[VIEW],
                        'Owner cannot view published content')
        self.assertFalse(owner_permissions[DELETE],
                         'Owner should retract, not delete published content')

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


class TestWorkspacePolicyConsumers(WorkspaceContentBaseTestCase):
    """Test modify permissions for policy: consumers
    """

    def setUp(self):
        WorkspaceContentBaseTestCase.setUp(self)
        self.workspace_folder.participant_policy = 'consumers'

    def test_draft_state(self):
        """
        draft content can only be modified by team manager and owner
        """
        admin_permissions = api.user.get_permissions(
            username='wsadmin',
            obj=self.document,
        )
        self.assertTrue(admin_permissions[MODIFY],
                        'Admin cannot modify draft content')

        member_permissions = api.user.get_permissions(
            username='wsmember',
            obj=self.document,
        )
        self.assertFalse(member_permissions[MODIFY],
                         'Member can modify draft content')

        owner_permissions = api.user.get_permissions(
            username='wsmember',
            obj=self.document2,
        )
        self.assertTrue(owner_permissions[MODIFY],
                        'Owner cannot modify draft content')

        nonmember_permissions = api.user.get_permissions(
            username='nonmember',
            obj=self.document,
        )
        self.assertFalse(nonmember_permissions[MODIFY],
                         'Non-member can modify draft content')
        logout()
        anon_permissions = api.user.get_permissions(
            obj=self.document,
        )
        self.assertFalse(anon_permissions[MODIFY],
                         'Anonymous can modify draft content')

    def test_pending_state(self):
        """
        pending content can only be modified by team manager
        """
        api.content.transition(self.document, 'submit')
        api.content.transition(self.document2, 'submit')

        admin_permissions = api.user.get_permissions(
            username='wsadmin',
            obj=self.document,
        )
        self.assertTrue(admin_permissions[MODIFY],
                        'Admin cannot modify pending content')

        member_permissions = api.user.get_permissions(
            username='wsmember',
            obj=self.document,
        )
        self.assertFalse(member_permissions[MODIFY],
                         'Member can modify pending content')

        owner_permissions = api.user.get_permissions(
            username='wsmember',
            obj=self.document2,
        )
        self.assertFalse(owner_permissions[MODIFY],
                         'Owner can modify pending content')

        nonmember_permissions = api.user.get_permissions(
            username='nonmember',
            obj=self.document,
        )
        self.assertFalse(nonmember_permissions[MODIFY],
                         'Non-member can modify pending content')
        logout()
        anon_permissions = api.user.get_permissions(
            obj=self.document,
        )
        self.assertFalse(anon_permissions[MODIFY],
                         'Anonymous can modify pending content')

    def test_published_state(self):
        """
        published content can only be modified by team manager
        """
        api.content.transition(self.document, 'submit')
        api.content.transition(self.document, 'publish')
        api.content.transition(self.document2, 'submit')
        api.content.transition(self.document2, 'publish')

        admin_permissions = api.user.get_permissions(
            username='wsadmin',
            obj=self.document,
        )
        self.assertTrue(admin_permissions[MODIFY],
                        'Admin cannot modify published content')

        member_permissions = api.user.get_permissions(
            username='wsmember',
            obj=self.document,
        )
        self.assertFalse(member_permissions[MODIFY],
                         'member can modify published content')

        owner_permissions = api.user.get_permissions(
            username='wsmember',
            obj=self.document2,
        )
        self.assertFalse(owner_permissions[MODIFY],
                         'Owner can modify published content')

        nonmember_permissions = api.user.get_permissions(
            username='nonmember',
            obj=self.document,
        )
        self.assertFalse(nonmember_permissions[MODIFY],
                         'user can modify workspace content')

        logout()
        anon_permissions = api.user.get_permissions(
            obj=self.document,
        )
        self.assertFalse(anon_permissions[MODIFY],
                         'Anonymous can modify draft content')


class TestWorkspacePolicyProducers(TestWorkspacePolicyConsumers):
    """Modify permission is identical to Consumers
    """

    def setUp(self):
        super(TestWorkspacePolicyProducers, self).setUp()
        self.workspace_folder.participant_policy = 'producers'


class TestWorkspacePolicyPublishers(TestWorkspacePolicyConsumers):
    """Modify permission is identical to Consumers
    """

    def setUp(self):
        super(TestWorkspacePolicyPublishers, self).setUp()
        self.workspace_folder.participant_policy = 'publishers'


class TestWorkspacePolicyModerators(WorkspaceContentBaseTestCase):
    """
    Moderators allows teammembers to edit other people's content.
    Different test set, don't inherit but do all tests explicitly.
    """

    def setUp(self):
        WorkspaceContentBaseTestCase.setUp(self)
        self.workspace_folder.participant_policy = 'moderators'

    def test_draft_state(self):
        """
        In moderators, all content can be modified by
        teammanager, teammember and owner.
        """
        admin_permissions = api.user.get_permissions(
            username='wsadmin',
            obj=self.document,
        )
        self.assertTrue(admin_permissions[MODIFY],
                        'Admin cannot modify draft content')

        member_permissions = api.user.get_permissions(
            username='wsmember',
            obj=self.document,
        )
        self.assertTrue(member_permissions[MODIFY],
                        'Member cannot modify draft content')

        owner_permissions = api.user.get_permissions(
            username='wsmember',
            obj=self.document2,
        )
        self.assertTrue(owner_permissions[MODIFY],
                        'Owner cannot modify draft content')

        nonmember_permissions = api.user.get_permissions(
            username='nonmember',
            obj=self.document,
        )
        self.assertFalse(nonmember_permissions[MODIFY],
                         'Non-member can modify draft content')
        logout()
        anon_permissions = api.user.get_permissions(
            obj=self.document,
        )
        self.assertFalse(anon_permissions[MODIFY],
                         'Anonymous can modify draft content')

    def test_pending_state(self):
        """
        In moderators, all content can be modified by
        teammanager, teammember and owner.
        """
        api.content.transition(self.document, 'submit')
        api.content.transition(self.document2, 'submit')

        admin_permissions = api.user.get_permissions(
            username='wsadmin',
            obj=self.document,
        )
        self.assertTrue(admin_permissions[MODIFY],
                        'Admin cannot modify pending content')

        member_permissions = api.user.get_permissions(
            username='wsmember',
            obj=self.document,
        )
        self.assertTrue(member_permissions[MODIFY],
                        'Member cannot modify pending content')

        owner_permissions = api.user.get_permissions(
            username='wsmember',
            obj=self.document2,
        )
        self.assertTrue(owner_permissions[MODIFY],
                        'Owner cannot modify pending content')

        nonmember_permissions = api.user.get_permissions(
            username='nonmember',
            obj=self.document,
        )
        self.assertFalse(nonmember_permissions[MODIFY],
                         'Non-member can modify pending content')
        logout()
        anon_permissions = api.user.get_permissions(
            obj=self.document,
        )
        self.assertFalse(anon_permissions[MODIFY],
                         'Anonymous can modify pending content')

    def test_published_state(self):
        """
        In moderators, all content can be modified by
        teammanager, teammember and owner.
        """
        api.content.transition(self.document, 'submit')
        api.content.transition(self.document, 'publish')
        api.content.transition(self.document2, 'submit')
        api.content.transition(self.document2, 'publish')

        admin_permissions = api.user.get_permissions(
            username='wsadmin',
            obj=self.document,
        )
        self.assertTrue(admin_permissions[MODIFY],
                        'Admin cannot modify published content')

        member_permissions = api.user.get_permissions(
            username='wsmember',
            obj=self.document,
        )
        self.assertTrue(member_permissions[MODIFY],
                        'member cannot modify published content')

        owner_permissions = api.user.get_permissions(
            username='wsmember',
            obj=self.document2,
        )
        self.assertTrue(owner_permissions[MODIFY],
                        'Owner cannot modify published content')

        nonmember_permissions = api.user.get_permissions(
            username='nonmember',
            obj=self.document,
        )
        self.assertFalse(nonmember_permissions[MODIFY],
                         'user can modify workspace content')

        logout()
        anon_permissions = api.user.get_permissions(
            obj=self.document,
        )
        self.assertFalse(anon_permissions[MODIFY],
                         'Anonymous can modify draft content')
