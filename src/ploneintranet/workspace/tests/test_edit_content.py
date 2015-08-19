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
        workspace_folder = api.content.create(
            workspaces,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace'
        )
        self.folder = api.content.create(
            workspace_folder,
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
