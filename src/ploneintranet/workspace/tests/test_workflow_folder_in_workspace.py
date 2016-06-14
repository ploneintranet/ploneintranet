# coding=utf-8
from plone import api
from ploneintranet.workspace.tests.base import BaseTestCase

VIEW = 'View'
DELETE = 'Delete objects'
MODIFY = 'Modify portal content'

"""
This tests the workflow of a folder in a workspacefolder.
Workflow of the workspace itself is tested elsewhere
in test_workflow_workspace.
"""


class TestFolderWorkflow(BaseTestCase):

    def test_default_workflow(self):
        """
        the folder_in_workspace_workflow should be listed as a workflow
        """
        self.assertIn(
            'folder_in_workspace_workflow',
            self.portal_workflow.listWorkflows()
        )
        # Default workflow should be set
        self.assertTupleEqual(
            self.portal_workflow.getDefaultChain(),
            ('simple_publication_workflow',)
        )

    def test_default_workflow_for_folders(self):
        ''' Test that a folder created in the portal
        has the default workflow applied
        '''
        self.login_as_portal_owner()
        wftool = self.portal_workflow

        # Check that a folder has the default workflow outside workspaces
        folder_in_portal = api.content.create(
            self.portal,
            'Folder',
            'test-folder-in-portal'
        )
        self.assertListEqual(
            ['simple_publication_workflow'],
            [x.getId() for x in wftool.getWorkflowsFor(folder_in_portal)],
        )

    def test_placeful_workflow(self):
        """
        The folder_in_workspace_workflow should be applied automatically to
        folders created inside a workspace
        """
        self.login_as_portal_owner()
        wftool = self.portal_workflow
        # A folder in the workspace should have
        # the folder_in_workspace_workflow
        workspace = api.content.create(
            self.workspace_container,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace'
        )
        folder_in_workspace = api.content.create(
            workspace,
            'Folder',
            'test-folder-in-ws'
        )
        self.assertListEqual(
            ['folder_in_workspace_workflow'],
            [x.getId() for x in wftool.getWorkflowsFor(folder_in_workspace)]
        )


class TestSecretWorkspaceContentWorkflow(BaseTestCase):

    # properly set this ones to change workspacefolder behavior
    _participant_policy = 'producers'
    _fire_transition = None
    _expected_review_state = 'secret'

    # These are the general permission that are almopst
    # common to every test case
    _base_permissions_by_userid = {
        'wsadmin': {VIEW, MODIFY, DELETE},
        'wsowner': {VIEW, MODIFY},
        'wsmember': {VIEW},
        'nonmember': set(),
        None: set(),  # anonymous
    }
    # but your test case may override this
    _test_specific_permissions_by_userid = {}

    def setUp(self):
        BaseTestCase.setUp(self)
        self.login_as_portal_owner()
        api.user.create(username='wsadmin', email="admin@test.com")
        api.user.create(username='wsmember', email="member@test.com")
        api.user.create(username='wsowner', email="owner@test.com")
        api.user.create(username='nonmember', email="user@test.com")

        self.workspace_folder = api.content.create(
            self.workspace_container,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace',
            title='Welcome to my workspace')

        # Allow the users to create testing content
        # This policy, will be then reset to fit the testcase
        self.workspace_folder.participant_policy = 'producers'

        self.add_user_to_workspace('wsmember', self.workspace_folder)
        self.add_user_to_workspace('wsowner', self.workspace_folder)
        self.add_user_to_workspace(
            'wsadmin', self.workspace_folder, {'Admins'}
        )

        self.login('wsowner')
        self.folder_in_workspace = api.content.create(
            self.workspace_folder,
            'Folder',
            'owner-folder'
        )
        self.login_as_portal_owner()
        # Finally change the workspace folder policy and (eventually) its state
        self.workspace_folder.participant_policy = self._participant_policy
        if self._fire_transition:
            api.content.transition(
                self.workspace_folder,
                self._fire_transition
            )

    def get_expected_permissions_for(self, userid):
        ''' Get the permission for the given userid (None => anonymous)

        First look in _test_specific_permissions_by_userid then in
        _base_permissions_by_userid.
        '''
        return self._test_specific_permissions_by_userid.get(
            userid,
            self._base_permissions_by_userid[userid]
        )

    def check_permissions_for(self, userid):
        permissions = api.user.get_permissions(
            username=userid,
            obj=self.folder_in_workspace
        )
        observed = {key for key in [VIEW, DELETE, MODIFY] if permissions[key]}
        expected = self.get_expected_permissions_for(userid)
        self.assertSetEqual(observed, expected)

    def test_admin_permissions(self):
        self.check_permissions_for('wsadmin'),

    def test_owner_permissions(self):
        self.check_permissions_for('wsowner'),

    def test_member_permissions(self):
        self.check_permissions_for('wsmember'),

    def test_nonmember_permissions(self):
        self.check_permissions_for('nonmember'),

    def test_anonymous_permissions(self):
        self.logout()
        self.check_permissions_for(None),

    def test_setup_workflow_state(self):
        self.assertEqual(
            api.content.get_state(self.workspace_folder),
            self._expected_review_state,
            'workspace is in incorrect state'
        )


class TestPrivateWorkspaceContentWorkflow(TestSecretWorkspaceContentWorkflow):
    """
    Content in a private workspace should have the same security
    View protections as content in a secret workspace.
    Inherit the test.
    """
    _fire_transition = 'make_private'
    _expected_review_state = 'private'


class TestOpenWorkspaceContentWorkflow(TestSecretWorkspaceContentWorkflow):
    """
    Content in an open workspace has different View settings.
    re-implement all test methods.

    all team members should be able to see published content,
    regular plone users should also.
    Only team managers should be able to delete published content
    """
    _fire_transition = 'make_open'
    _expected_review_state = 'open'

    _test_specific_permissions_by_userid = {
        'nonmember': {VIEW}
    }


class TestWorkspacePolicyConsumers(TestSecretWorkspaceContentWorkflow):
    """Test modify permissions for policy: consumers
    """
    _participant_policy = 'consumers'
    _test_specific_permissions_by_userid = {
        'owner': set(),
    }


class TestWorkspacePolicyProducers(TestWorkspacePolicyConsumers):
    """Modify permission is identical to Consumers
    """
    _participant_policy = 'producers'


class TestWorkspacePolicyPublishers(TestWorkspacePolicyConsumers):
    """Modify permission is identical to Consumers
    """
    _participant_policy = 'publishers'


class TestWorkspacePolicyModerators(TestSecretWorkspaceContentWorkflow):
    """
    Moderators allows teammembers to edit other people's content.
    """
    _participant_policy = 'moderators'
    _test_specific_permissions_by_userid = {
        'wsowner': {VIEW, MODIFY, DELETE},
        'wsmember': {VIEW, MODIFY, DELETE},
    }
