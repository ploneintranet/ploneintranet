# -*- coding: utf-8 -*-
from plone import api
from ploneintranet.workspace.tests.base import FunctionalBaseTestCase


class TestEditContent(FunctionalBaseTestCase):

    def setUp(self):
        super(TestEditContent, self).setUp()
        self.login_as_portal_owner()
        workspaces = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacecontainer',
            'example-workspace-container'
        )
        self.workspace_folder = api.content.create(
            workspaces,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace'
        )
        self.workspace_folder.participant_policy = 'producers'
        api.user.create(username='user1', email='test@test.com')
        api.user.create(username='user2', email='toast@test.com')
        self.add_user_to_workspace(
            'user1',
            self.workspace_folder,
        )
        self.add_user_to_workspace(
            'user2',
            self.workspace_folder,
        )
        self.logout()
        self.login('user1')
        self.folder = api.content.create(
            self.workspace_folder,
            'Folder',
            'example-folder',
            title='Example folder',
            description='Example description',
        )

        # Commit so the testbrowser can see the folder
        import transaction
        transaction.commit()

    def test_edit_folder_form(self):
        form = api.content.get_view(
            'edit_folder', self.folder, self.request)
        result = form()
        self.assertIn('Change folder title and description', result)
        self.assertIn('<button id="form-buttons-edit"', result)

    def test_edit_folder(self):
        self.browser_login_as_site_administrator()
        self.browser.open('%s/@@edit_folder' % self.folder.absolute_url())
        self.assertEqual(
            self.browser.getControl(name='title').value,
            'Example folder')
        self.assertEqual(
            self.browser.getControl(name='description').value,
            'Example description')
        self.browser.getControl(name='title').value = 'Nice folder'
        self.browser.getControl(name='description').value = 'Nice description'
        self.browser.getControl(name='form.buttons.edit').click()
        self.assertEqual(self.folder.Title(), 'Nice folder')
        self.assertEqual(self.folder.Description(), 'Nice description')

    def test_no_owner_role_inheritance_on_content(self):
        """
        user1 has created the folder. If user2 creates content in this folder,
        user1 must not have the Owner role via inheritance on it.
        """
        self.login('user2')
        document = api.content.create(
            self.folder,
            'Document',
            'example-document',
            title='Example document',
            description='Example description',
        )
        self.logout()
        self.login('user1')
        local_roles = api.user.get_roles(obj=document)
        self.assertNotIn('Owner', local_roles)
