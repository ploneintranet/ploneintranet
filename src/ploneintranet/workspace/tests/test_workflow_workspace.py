from AccessControl import Unauthorized
from ploneintranet.workspace.tests.base import BaseTestCase
from plone import api
from ploneintranet.workspace.browser.add_workspace import AddWorkspace

VIEW = 'View'
ACCESS = 'Access contents information'
MODIFY = 'Modify portal content'
MANAGE = 'ploneintranet.workspace: Manage workspace'
ADD_CONTENT = 'Add portal content'
ADD_STATUS = 'Plone Social: Add Microblog Status Update'
VIEW_STATUS = 'Plone Social: View Microblog Status Update'
MODIFY_OWN_STATUS = 'Plone Social: Modify Own Microblog Status Update'
MODIFY_STATUS = 'Plone Social: Modify Microblog Status Update'
DELETE_OWN_STATUS = 'Plone Social: Delete Own Microblog Status Update'
DELETE_STATUS = 'Plone Social: Delete Microblog Status Update'

"""
This tests the workflow of the workspacefolder itself.
Workflow on content within the workspace is tested elsewhere
in test_workflow_workspace_content, and for case content in
test_workflow_case_content.
"""


class TestWorkSpaceWorkflow(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)
        self.login_as_portal_owner()
        self.open_workspaces = api.content.create(
            type="ploneintranet.workspace.workspacecontainer",
            title="Open Workspaces",
            container=self.portal,
        )
        self.restricted_workspaces = api.content.create(
            type="ploneintranet.workspace.workspacecontainer",
            title="Restricted Workspaces",
            container=self.portal,
        )
        api.content.transition(self.restricted_workspaces,
                               'restrict')

        api.user.create(username='noaddrights', email="noaddrights@test.com")
        api.user.create(username='hasaddrights', email="hasaddrights@test.com")
        api.user.grant_roles(
            username='hasaddrights',
            obj=self.restricted_workspaces,
            roles=['Contributor'],
        )
        api.user.create(username='nonmember', email="user@test.com")
        api.user.create(username='wsmember', email="member@test.com")
        api.user.create(username='wsadmin', email="admin@test.com")
        self.workspace_container = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacecontainer',
            'example-workspace-container',
            title='Welcome to my example workspace container'
        )
        self.workspace_folder = api.content.create(
            self.workspace_container,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace',
            title='Welcome to my workspace'
        )
        self.add_user_to_workspace('wsmember', self.workspace_folder)
        self.add_user_to_workspace('wsadmin', self.workspace_folder,
                                   set(['Admins']))
        # A workspace editor
        api.user.create(username='wseditor', email='wseditor@test.com')
        self.add_user_to_workspace('wseditor', self.workspace_folder)
        # Grant them the Editor role on the workspace
        api.user.grant_roles(
            username='wseditor',
            obj=self.workspace_folder,
            roles=['Editor'],
        )

    def admin_permissions(self, permission):
        permissions = api.user.get_permissions(
            username='wsadmin',
            obj=self.workspace_folder,
        )
        return permissions[permission]

    def editor_permissions(self, permission):
        permissions = api.user.get_permissions(
            username='wseditor',
            obj=self.workspace_folder,
        )
        return permissions[permission]

    def member_permissions(self, permission):
        permissions = api.user.get_permissions(
            username='wsmember',
            obj=self.workspace_folder,
        )
        return permissions[permission]

    def nonmember_permissions(self, permission):
        permissions = api.user.get_permissions(
            username='nonmember',
            obj=self.workspace_folder,
        )
        return permissions[permission]

    def anon_permissions(self, permission):
        self.logout()
        permissions = api.user.get_permissions(
            obj=self.workspace_folder,
        )
        return permissions[permission]

    def test_create_workspace_open(self):
        """
        Test creation of a workspace
        """
        # open system. Workspaces folder is open for authenticated
        self.login('noaddrights')
        request = self.layer['request'].clone()
        request.form['workspace-type'] = 'private'
        request.form['title'] = 'everybody can add'
        ac = AddWorkspace(self.open_workspaces, request)
        ac()
        self.assertIn('everybody-can-add',
                      self.open_workspaces.objectIds())

    def test_create_workspace_restricted_nocaccess(self):
        """
        Test creation of a workspace
        """
        self.assertNotIn(
            'Contributor',
            api.user.get_roles(username='noaddrights',
                               obj=self.restricted_workspaces)
        )
        self.login('noaddrights')
        request = self.layer['request'].clone()
        request.form['workspace-type'] = 'private'
        request.form['title'] = 'not anyone is permitted'
        ac = AddWorkspace(self.restricted_workspaces, request)
        with self.assertRaises(Unauthorized):
            ac()
        self.logout()

    def test_create_workspace_restricted_contributor(self):
        """
        Test creation of a workspace
        """
        self.assertIn(
            'Contributor',
            api.user.get_roles(username='hasaddrights',
                               obj=self.restricted_workspaces)
        )
        self.login('hasaddrights')
        request = self.layer['request'].clone()
        request.form['workspace-type'] = 'private'
        request.form['title'] = 'can-add-when-contributor'
        ac = AddWorkspace(self.restricted_workspaces, request)
        ac()
        self.assertIn('can-add-when-contributor',
                      self.restricted_workspaces.objectIds())

        self.logout()

    def test_private_workspace(self):
        """
        Private workspaces should be visible and accessible
        only to members.
        NOTE: Non-members should be able to request access. Therefore they need
        limited access to some attributes of the workspace like Title.
        This scenario is NOT tested here yet.
        """
        api.content.transition(self.workspace_folder,
                               'make_private')

        self.assertTrue(self.admin_permissions(VIEW))
        self.assertTrue(self.admin_permissions(ACCESS))
        self.assertTrue(self.admin_permissions(ADD_STATUS))
        self.assertTrue(self.admin_permissions(VIEW_STATUS))

        self.assertTrue(self.member_permissions(VIEW))
        self.assertTrue(self.member_permissions(ACCESS))
        self.assertTrue(self.member_permissions(ADD_STATUS))
        self.assertTrue(self.member_permissions(VIEW_STATUS))

        self.assertFalse(self.nonmember_permissions(VIEW))
        self.assertFalse(self.nonmember_permissions(ACCESS))
        self.assertFalse(self.nonmember_permissions(ADD_STATUS))
        self.assertFalse(self.nonmember_permissions(VIEW_STATUS))

        self.assertFalse(self.anon_permissions(VIEW))
        self.assertFalse(self.anon_permissions(ACCESS))
        self.assertFalse(self.anon_permissions(ADD_STATUS))
        self.assertFalse(self.anon_permissions(VIEW_STATUS))

    def test_secret_workspace(self):
        """
        Secret workspaces should be invisible to all but members
        """
        # default state is secret
        self.assertEqual(api.content.get_state(self.workspace_folder),
                         'secret')

        self.assertTrue(self.admin_permissions(VIEW))
        self.assertTrue(self.admin_permissions(ACCESS))
        self.assertTrue(self.admin_permissions(ADD_STATUS))
        self.assertTrue(self.admin_permissions(VIEW_STATUS))

        self.assertTrue(self.member_permissions(VIEW))
        self.assertTrue(self.member_permissions(ACCESS))
        self.assertTrue(self.member_permissions(ADD_STATUS))
        self.assertTrue(self.member_permissions(VIEW_STATUS))

        self.assertFalse(self.nonmember_permissions(VIEW))
        self.assertFalse(self.nonmember_permissions(ACCESS))
        self.assertFalse(self.nonmember_permissions(ADD_STATUS))
        self.assertFalse(self.nonmember_permissions(VIEW_STATUS))

        self.assertFalse(self.anon_permissions(VIEW))
        self.assertFalse(self.anon_permissions(ACCESS))
        self.assertFalse(self.anon_permissions(ADD_STATUS))
        self.assertFalse(self.anon_permissions(VIEW_STATUS))

    def test_open_workspace(self):
        """
        Open workspaces should be visible
        and accessible to all users

        Content within open workspace is also visible
        to all users
        """
        api.content.transition(self.workspace_folder,
                               'make_open')

        self.assertTrue(self.admin_permissions(VIEW))
        self.assertTrue(self.admin_permissions(ACCESS))
        self.assertTrue(self.admin_permissions(ADD_STATUS))
        self.assertTrue(self.admin_permissions(VIEW_STATUS))

        self.assertTrue(self.member_permissions(VIEW))
        self.assertTrue(self.member_permissions(ACCESS))
        self.assertTrue(self.member_permissions(ADD_STATUS))
        self.assertTrue(self.member_permissions(VIEW_STATUS))

        self.assertTrue(self.nonmember_permissions(VIEW))
        self.assertTrue(self.nonmember_permissions(ACCESS))
        self.assertFalse(self.nonmember_permissions(ADD_STATUS))
        self.assertTrue(self.nonmember_permissions(VIEW_STATUS))

        self.assertFalse(self.anon_permissions(VIEW))
        self.assertFalse(self.anon_permissions(ACCESS))
        self.assertFalse(self.anon_permissions(ADD_STATUS))
        self.assertFalse(self.anon_permissions(VIEW_STATUS))

    def test_modify_workspace(self):
        """
        Only a Workspace Admin should be able to edit the workspace.
        A user with the Editor role should not be able
        to edit the workspace itself (only the content within a workspace)
        """

        self.assertTrue(self.admin_permissions(MODIFY))

        # Editor cannot edit workspace itself, only content within
        self.assertFalse(self.editor_permissions(MODIFY))
        self.assertFalse(self.member_permissions(MODIFY))
        self.assertFalse(self.nonmember_permissions(MODIFY))
        self.assertFalse(self.anon_permissions(MODIFY))

    def test_manage_workspace(self):
        """
        A Workspace Admin should have the manage workspace permission
        """
        self.assertTrue(self.admin_permissions(MANAGE))
        self.assertFalse(self.member_permissions(MANAGE))
        self.assertFalse(self.nonmember_permissions(MANAGE))
        self.assertFalse(self.anon_permissions(MANAGE))

    def test_workspace_transitions(self):
        """
        A Workspace Admin should be able to change the state of a workspace
        """
        self.assertTrue(self.admin_permissions(MANAGE))
        self.assertFalse(self.member_permissions(MANAGE))
        self.assertFalse(self.nonmember_permissions(MANAGE))
        self.assertFalse(self.anon_permissions(MANAGE))

        # The Admin should be able to transition the workspace
        # through each state
        self.login('wsadmin')

        api.content.transition(self.workspace_folder,
                               'make_private')
        self.assertEqual(api.content.get_state(self.workspace_folder),
                         'private')

        api.content.transition(self.workspace_folder,
                               'make_open')
        self.assertEqual(api.content.get_state(self.workspace_folder),
                         'open')

        api.content.transition(self.workspace_folder,
                               'make_secret')
        self.assertEqual(api.content.get_state(self.workspace_folder),
                         'secret')

    def test_workspace_statusupdate_siteadmin(self):
        """Site admin should retain manage statusupdate permissions"""
        # logged in as global admin
        permissions = api.user.get_permissions(
            obj=self.workspace_folder,
        )
        self.assertIn(MODIFY_STATUS, permissions)
        self.assertIn(DELETE_STATUS, permissions)

    def test_workspace_statusupdate_teamadmin(self):
        """Team admin should gain manage statusupdate permissions"""
        self.assertTrue(self.admin_permissions(MODIFY_STATUS))
        self.assertTrue(self.admin_permissions(DELETE_STATUS))

    def test_workspace_statusupdate_teammember(self):
        """Member should retain global own statusupdate permissions"""
        self.assertTrue(self.member_permissions(MODIFY_OWN_STATUS))
        self.assertTrue(self.member_permissions(DELETE_OWN_STATUS))
        self.assertFalse(self.member_permissions(MODIFY_STATUS))
        self.assertFalse(self.member_permissions(DELETE_STATUS))


class TestWorkSpaceContainerWorkflow(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)
        self.login_as_portal_owner()
        api.user.create(username='normal_user', email="user@test.com")
        api.user.create(
            username='contributor', email="contributor@test.com",
            roles=('Member', 'Contributor'))

    def test_open_workspacecontainer(self):
        """
        Check that WorkspaceContainer is by default open: all authenticated
        members can add content
        """
        self.login_as_portal_owner()
        workspace_folder = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacecontainer',
            'open-workspaces',
            title='Open Workspaces'
        )
        self.assertIn('open-workspaces', self.portal)

        # Authenticated should have the add content permission
        authenticated_permissions = api.user.get_permissions(
            username='normal_user',
            obj=workspace_folder,
        )
        self.assertTrue(
            authenticated_permissions[ADD_CONTENT],
            "Authenticated can't add content to an open workspace container"
        )

    def test_restricted_workspacecontainer(self):
        """
        Check that a restricted WorkspaceContainer prevents authenticated from
        adding content.
        """
        self.login_as_portal_owner()
        workspace_folder = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacecontainer',
            'restricted-workspaces',
            title='Restricted Workspaces'
        )
        self.assertIn('restricted-workspaces', self.portal)
        api.content.transition(obj=workspace_folder, transition='restrict')

        # Authenticated should not have the add content permission, but should
        # be able to view
        authenticated_permissions = api.user.get_permissions(
            username='normal_user',
            obj=workspace_folder,
        )
        self.assertFalse(
            authenticated_permissions[ADD_CONTENT],
            'Authenticated can add content to a restricted workspace container'
        )
        self.assertTrue(
            authenticated_permissions[VIEW],
            "Authenticated can't view a restricted workspace container"
        )
        self.assertTrue(
            authenticated_permissions[ACCESS],
            "Authenticated can't access a restricted workspace container"
        )

        # Contributor should have the add content permission
        contributor_permissions = api.user.get_permissions(
            username='contributor',
            obj=workspace_folder,
        )
        self.assertTrue(
            contributor_permissions[ADD_CONTENT],
            "Contributor can't add content to a restricted workspace container"
        )
