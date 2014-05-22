from plone import api
from plone.app.testing import logout
from ploneintranet.workspace.tests.base import BaseTestCase


class TestWorkflow(BaseTestCase):

    def test_default_workflow(self):
        """
        the ploneintranet workflow should be listed as a workflow
        """
        wftool = api.portal.get_tool('portal_workflow')
        self.assertIn('ploneintranet_workflow',
                      wftool.listWorkflows())
        # But no default workflow should be set
        self.assertFalse(wftool.getDefaultChain())

    def test_placeful_workflow(self):
        """
        The ploneintranet workflowshould be applied automatically to content
        in the workspace
        """
        self.login_as_portal_owner()
        wftool = api.portal.get_tool('portal_workflow')

        # Check that a document has the default workflow
        document = api.content.create(
            self.portal,
            'Document',
            'document-portal'
        )
        self.assertFalse(wftool.getWorkflowsFor(document))

        # A document in the workspace should have the workspace workflow
        workspace_folder = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace')

        document_workspace = api.content.create(
            workspace_folder,
            'Document',
            'document-workspace'
        )
        self.assertEqual('ploneintranet_workflow',
                         wftool.getWorkflowsFor(document_workspace)[0].id)

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

    def test_public_state(self):
        """
        all authenticated users should be able to see public content
        anonymous users should not
        """
        self.login_as_portal_owner()
        api.user.create(username='nonmember', email="user@test.com")
        api.user.create(username='wsmember', email="member@test.com")
        api.user.create(username='wsadmin', email="admin@test.com")
        workspace_folder = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace')
        api.content.transition(workspace_folder, 'make_private')
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
        api.content.transition(document, 'publish_public')

        admin_permissions = api.user.get_permissions(
            username='wsadmin',
            obj=document,
        )
        self.assertTrue(admin_permissions['View'],
                        'Admin cannot view restricted content')
        self.assertTrue(admin_permissions['Access contents information'],
                        'Admin cannot access restricted content')
        member_permissions = api.user.get_permissions(
            username='wsmember',
            obj=document,
        )
        self.assertTrue(member_permissions['View'],
                        'member cannot view restricted content')
        self.assertTrue(member_permissions['Access contents information'],
                        'member cannot access restricted content')
        user_permissions = api.user.get_permissions(
            username='nonmember',
            obj=document,
        )
        self.assertTrue(user_permissions['View'],
                        'user cannot view restricted workspace content')
        self.assertTrue(user_permissions['Access contents information'],
                        'user cannot access restricted workspace content')

        logout()
        anon_permissions = api.user.get_permissions(
            obj=document
        )
        self.assertFalse(anon_permissions['View'],
                         'anonymous can view restricted workspace content')
        self.assertFalse(anon_permissions['Access contents information'],
                         'anonymous can access restricted workspace content')

    def test_public_transition_private_workspace(self):
        """
        it should be possible to transition content to public in a private
        workspace
        """
        self.login_as_portal_owner()
        workspace_folder = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace')

        api.content.transition(workspace_folder,
                               'make_private')

        document = api.content.create(
            workspace_folder,
            'Document',
            'document1')

        api.content.transition(document,
                               'submit')
        api.content.transition(document,
                               'publish')

        # Publish to the public
        api.content.transition(document,
                               'publish_public')
        self.assertEqual(api.content.get_state(document),
                         'public')

        # Restrict to workspace members
        api.content.transition(document,
                               'restrict')
        self.assertEqual(api.content.get_state(document),
                         'published')

    def test_public_transition_secret_workspace(self):
        """
        it should not be possible to make content in a secret workspace public
        """
        self.login_as_portal_owner()
        workspace_folder = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace')

        document = api.content.create(
            workspace_folder,
            'Document',
            'document1')

        api.content.transition(document,
                               'submit')
        api.content.transition(document,
                               'publish')

        # It shouldn't be possible to transition the document to public
        with self.assertRaises(api.exc.InvalidParameterError):
            api.content.transition(document, 'publish_public')

        self.assertEqual(api.content.get_state(document),
                         'published')
