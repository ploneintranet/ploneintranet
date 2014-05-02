from plone import api
from ploneintranet.workspace.tests.base import BaseTestCase


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
        self.assertEqual(api.content.get_state(workspace_folder),
                         'secret',
                         'workspace is in incorrect state')
        self.add_user_to_workspace(
            'wsadmin',
            workspace_folder,
            set(['Admins']))
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

    def test_pending_state(self):
        """
        team managers should be able to view pending items,
        team members should not
        """
        self.login_as_portal_owner()
        api.user.create(username='wsmember', email="member@test.com")
        api.user.create(username='wsadmin', email="admin@test.com")
        workspace_folder = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace')
        self.add_user_to_workspace(
            'wsadmin',
            workspace_folder,
            set(['Admins']))
        self.add_user_to_workspace(
            'wsmember',
            workspace_folder)

        document = api.content.create(
            workspace_folder,
            'Document',
            'document1')
        api.content.transition(document, 'submit')

        admin_permissions = api.user.get_permissions(
            username='wsadmin',
            obj=document,
        )
        self.assertTrue(admin_permissions['View'],
                        'Admin cannot view pending content')
        member_permissions = api.user.get_permissions(
            username='wsmember',
            obj=document,
        )
        self.assertFalse(member_permissions['View'],
                         'member can view pending content')

    def test_published_state(self):
        """
        all team members should be able to see published content,
        regualar plone user should not
        """
        self.login_as_portal_owner()
        api.user.create(username='nonmember', email="user@test.com")
        api.user.create(username='wsmember', email="member@test.com")
        api.user.create(username='wsadmin', email="admin@test.com")
        workspace_folder = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace')
        self.add_user_to_workspace(
            'wsadmin',
            workspace_folder,
            set(['Admins']))
        self.add_user_to_workspace(
            'wsmember',
            workspace_folder)

        document = api.content.create(
            workspace_folder,
            'Document',
            'document1')
        api.content.transition(document, 'submit')
        api.content.transition(document, 'publish')

        admin_permissions = api.user.get_permissions(
            username='wsadmin',
            obj=document,
        )
        self.assertTrue(admin_permissions['View'],
                        'Admin cannot view published content')
        member_permissions = api.user.get_permissions(
            username='wsmember',
            obj=document,
        )
        self.assertTrue(member_permissions['View'],
                        'member cannot view published content')
        user_permissions = api.user.get_permissions(
            username='nonmember',
            obj=document,
        )
        self.assertFalse(user_permissions['View'],
                         'user can view workspace content')
