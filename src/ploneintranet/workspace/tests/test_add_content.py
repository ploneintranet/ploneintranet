# -*- coding: utf-8 -*-
from ploneintranet.workspace.browser.add_content import AddContent
from ploneintranet.workspace.browser.add_content import AddFolder
from plone import api
from ploneintranet.workspace.tests.base import FunctionalBaseTestCase


class TestAddContent(FunctionalBaseTestCase):

    def setUp(self):
        super(TestAddContent, self).setUp()
        self.login_as_portal_owner()
        workspace_folder = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace'
        )
        self.workspace = workspace_folder

        # Commit so the testbrowser can see the workspace
        import transaction
        transaction.commit()

    def test_add_content_form(self):
        form = api.content.get_view(
            'add_content', self.workspace, self.request)
        result = form()
        self.assertIn('Create document', result)
        self.assertIn('<button id="form-buttons-create"', result)

    def test_add_folder_form(self):
        form = api.content.get_view(
            'add_folder', self.workspace, self.request)
        result = form()
        self.assertIn('Create folder', result)
        self.assertIn('<button id="form-buttons-create"', result)

    def test_add_content_document(self):
        self.browser_login_as_site_administrator()
        self.browser.open('%s/@@add_content' % self.workspace.absolute_url())
        self.browser.getControl(name='title').value = 'Some Title'
        self.browser.getControl(name='description').value = 'My Desc'
        self.browser.getControl(name='form.buttons.create').click()
        new = self.workspace['some-title']
        self.assertEqual(new.portal_type, 'Document')
        self.assertEqual(new.title, u'Some Title')
        self.assertEqual(new.description, u'My Desc')

    def test_add_content_event(self):
        self.browser_login_as_site_administrator()
        self.browser.open('%s/@@add_content' % self.workspace.absolute_url())
        self.browser.getControl(name='portal_type').value = ['Event']
        self.browser.getControl(name='title').value = 'My Event'
        self.browser.getControl(name='form.buttons.create').click()
        new = self.workspace['my-event']
        self.assertEqual(new.portal_type, 'Event')

    def test_add_content_image(self):
        self.browser_login_as_site_administrator()
        self.browser.open('%s/@@add_content' % self.workspace.absolute_url())
        self.browser.getControl(name='portal_type').value = ['Image']
        self.browser.getControl(name='title').value = 'My Image'
        self.browser.getControl(name='form.buttons.create').click()
        new = self.workspace['my-image']
        self.assertEqual(new.portal_type, 'Image')

    def test_add_folder(self):
        self.browser_login_as_site_administrator()
        self.browser.open('%s/@@add_folder' % self.workspace.absolute_url())
        self.assertEqual(
            self.browser.getControl(name='portal_type').value, 'Folder')
        self.browser.getControl(name='title').value = 'My Folder'
        self.browser.getControl(name='form.buttons.create').click()
        new = self.workspace['my-folder']
        self.assertEqual(new.portal_type, 'Folder')
