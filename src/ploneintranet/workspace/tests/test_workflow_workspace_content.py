from plone import api
from ploneintranet.workspace.tests.base import BaseTestCase
from plone.app.testing import login
from plone.app.testing import logout

VIEW = 'View'
DELETE = 'Delete objects'
MODIFY = 'Modify portal content'

"""
This tests the workflow of content in a workspacefolder.
Workflow the workspace itself is tested elsewhere
in test_workflow_workspace.
"""


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

    def admin_permissions(self, permission):
        permissions = api.user.get_permissions(
            username='wsadmin',
            obj=self.document,
        )
        return permissions[permission]

    def member_permissions(self, permission):
        permissions = api.user.get_permissions(
            username='wsmember',
            obj=self.document,
        )
        return permissions[permission]

    def owner_permissions(self, permission):
        permissions = api.user.get_permissions(
            username='wsmember',
            obj=self.document2,
        )
        return permissions[permission]

    def nonmember_permissions(self, permission):
        permissions = api.user.get_permissions(
            username='nonmember',
            obj=self.document,
        )
        return permissions[permission]

    def anon_permissions(self, permission):
        logout()
        permissions = api.user.get_permissions(
            obj=self.document,
        )
        return permissions[permission]


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
        self.assertTrue(self.admin_permissions(VIEW))
        self.assertTrue(self.admin_permissions(DELETE))

        self.assertFalse(self.member_permissions(VIEW))
        self.assertFalse(self.member_permissions(DELETE))

        self.assertTrue(self.owner_permissions(VIEW))
        self.assertTrue(self.owner_permissions(DELETE))

        self.assertFalse(self.nonmember_permissions(VIEW))
        self.assertFalse(self.nonmember_permissions(DELETE))

        self.assertFalse(self.anon_permissions(VIEW))
        self.assertFalse(self.anon_permissions(DELETE))

    def test_pending_state(self):
        """
        team managers should be able to view pending items,
        team members should not
        team managers should be able to delete pending items, team members and
        owners should not
        """
        api.content.transition(self.document, 'submit')
        api.content.transition(self.document2, 'submit')

        self.assertTrue(self.admin_permissions(VIEW))
        self.assertTrue(self.admin_permissions(DELETE))

        self.assertFalse(self.member_permissions(VIEW))
        self.assertFalse(self.member_permissions(DELETE))

        self.assertTrue(self.owner_permissions(VIEW))
        self.assertFalse(self.owner_permissions(DELETE))

        self.assertFalse(self.nonmember_permissions(VIEW))
        self.assertFalse(self.nonmember_permissions(DELETE))

        self.assertFalse(self.anon_permissions(VIEW))
        self.assertFalse(self.anon_permissions(DELETE))

    def test_published_state(self):
        """
        all team members should be able to see published content,
        regular plone user should not
        it can only be deleted by the team manager
        """
        api.content.transition(self.document, 'submit')
        api.content.transition(self.document, 'publish')
        api.content.transition(self.document2, 'submit')
        api.content.transition(self.document2, 'publish')

        self.assertTrue(self.admin_permissions(VIEW))
        self.assertTrue(self.admin_permissions(DELETE))

        self.assertTrue(self.member_permissions(VIEW))
        self.assertFalse(self.member_permissions(DELETE))

        self.assertTrue(self.owner_permissions(VIEW))
        self.assertFalse(self.owner_permissions(DELETE))

        self.assertFalse(self.nonmember_permissions(VIEW))
        self.assertFalse(self.nonmember_permissions(DELETE))

        self.assertFalse(self.anon_permissions(VIEW))
        self.assertFalse(self.anon_permissions(DELETE))


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
        draft content can only be deleted by a team manager and owner
        """
        self.assertTrue(self.admin_permissions(VIEW))
        self.assertTrue(self.admin_permissions(DELETE))

        self.assertFalse(self.member_permissions(VIEW))
        self.assertFalse(self.member_permissions(DELETE))

        self.assertTrue(self.owner_permissions(VIEW))
        self.assertTrue(self.owner_permissions(DELETE))

        self.assertFalse(self.nonmember_permissions(VIEW))
        self.assertFalse(self.nonmember_permissions(DELETE))

        self.assertFalse(self.anon_permissions(VIEW))
        self.assertFalse(self.anon_permissions(DELETE))

    def test_pending_state(self):
        """
        team managers and owners should be able to view pending items,
        team members should not
        team managers should be able to delete pending items,
        team members and owners should not
        """
        api.content.transition(self.document, 'submit')
        api.content.transition(self.document2, 'submit')

        self.assertTrue(self.admin_permissions(VIEW))
        self.assertTrue(self.admin_permissions(DELETE))

        self.assertFalse(self.member_permissions(VIEW))
        self.assertFalse(self.member_permissions(DELETE))

        self.assertTrue(self.owner_permissions(VIEW))
        self.assertFalse(self.owner_permissions(DELETE))

        self.assertFalse(self.nonmember_permissions(VIEW))
        self.assertFalse(self.nonmember_permissions(DELETE))

        self.assertFalse(self.anon_permissions(VIEW))
        self.assertFalse(self.anon_permissions(DELETE))

    def test_published_state(self):
        """
        all team members should be able to see published content,
        regular plone users should also.
        Only team managers should be able to delete published content
        """
        api.content.transition(self.document, 'submit')
        api.content.transition(self.document, 'publish')
        api.content.transition(self.document2, 'submit')
        api.content.transition(self.document2, 'publish')

        self.assertTrue(self.admin_permissions(VIEW))
        self.assertTrue(self.admin_permissions(DELETE))

        self.assertTrue(self.member_permissions(VIEW))
        self.assertFalse(self.member_permissions(DELETE))

        self.assertTrue(self.owner_permissions(VIEW))
        self.assertFalse(self.owner_permissions(DELETE))

        self.assertTrue(self.nonmember_permissions(VIEW))
        self.assertFalse(self.nonmember_permissions(DELETE))

        self.assertFalse(self.anon_permissions(VIEW))
        self.assertFalse(self.anon_permissions(VIEW))


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
        self.assertTrue(self.admin_permissions(MODIFY))
        self.assertFalse(self.member_permissions(MODIFY))
        self.assertTrue(self.owner_permissions(MODIFY))
        self.assertFalse(self.nonmember_permissions(MODIFY))
        self.assertFalse(self.anon_permissions(MODIFY))

    def test_pending_state(self):
        """
        pending content can only be modified by team manager
        """
        api.content.transition(self.document, 'submit')
        api.content.transition(self.document2, 'submit')

        self.assertTrue(self.admin_permissions(MODIFY))
        self.assertFalse(self.member_permissions(MODIFY))
        self.assertFalse(self.owner_permissions(MODIFY))
        self.assertFalse(self.nonmember_permissions(MODIFY))
        self.assertFalse(self.anon_permissions(MODIFY))

    def test_published_state(self):
        """
        published content can only be modified by team manager
        """
        api.content.transition(self.document, 'submit')
        api.content.transition(self.document, 'publish')
        api.content.transition(self.document2, 'submit')
        api.content.transition(self.document2, 'publish')

        self.assertTrue(self.admin_permissions(MODIFY))
        self.assertFalse(self.member_permissions(MODIFY))
        self.assertFalse(self.owner_permissions(MODIFY))
        self.assertFalse(self.nonmember_permissions(MODIFY))
        self.assertFalse(self.anon_permissions(MODIFY))


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
        self.assertTrue(self.admin_permissions(MODIFY))
        self.assertTrue(self.member_permissions(MODIFY))
        self.assertTrue(self.owner_permissions(MODIFY))
        self.assertFalse(self.nonmember_permissions(MODIFY))
        self.assertFalse(self.anon_permissions(MODIFY))

    def test_pending_state(self):
        """
        In moderators, all content can be modified by
        teammanager, teammember and owner.
        """
        api.content.transition(self.document, 'submit')
        api.content.transition(self.document2, 'submit')

        self.assertTrue(self.admin_permissions(MODIFY))
        self.assertTrue(self.member_permissions(MODIFY))
        self.assertTrue(self.owner_permissions(MODIFY))
        self.assertFalse(self.nonmember_permissions(MODIFY))
        self.assertFalse(self.anon_permissions(MODIFY))

    def test_published_state(self):
        """
        In moderators, all content can be modified by
        teammanager, teammember and owner.
        """
        api.content.transition(self.document, 'submit')
        api.content.transition(self.document, 'publish')
        api.content.transition(self.document2, 'submit')
        api.content.transition(self.document2, 'publish')

        self.assertTrue(self.admin_permissions(MODIFY))
        self.assertTrue(self.member_permissions(MODIFY))
        self.assertTrue(self.owner_permissions(MODIFY))
        self.assertFalse(self.nonmember_permissions(MODIFY))
        self.assertFalse(self.anon_permissions(MODIFY))
