# -*- coding: utf-8 -*-
from plone import api
from ploneintranet.workspace.tests.base import FunctionalBaseTestCase
import os
import unittest


class TestAddContent(FunctionalBaseTestCase):

    def setUp(self):
        super(TestAddContent, self).setUp()
        self.login_as_portal_owner()
        self.workspace_container = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacecontainer',
            'example-workspace-container'
        )
        workspace_folder = api.content.create(
            self.workspace_container,
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

    @unittest.skip('For now events are not added using this view.')
    def test_add_content_event(self):
        self.browser_login_as_site_administrator()
        self.browser.open('%s/@@add_content' % self.workspace.absolute_url())
        self.browser.getControl(name='portal_type').value = ['Event']
        self.browser.getControl(name='title').value = 'My Event'
        self.browser.getControl(name='form.buttons.create').click()
        new = self.workspace['my-event']
        self.assertEqual(new.portal_type, 'Event')

    @unittest.skip('Broken IAppLayer test setup. Works when tested manually.')
    def test_add_content_image(self):
        self.browser_login_as_site_administrator()
        self.browser.open('%s/@@add_content' % self.workspace.absolute_url())
        self.browser.getControl(name='portal_type').value = ['Image']
        self.browser.getControl(name='title').value = 'My Image'
        self.browser.getControl(name='form.buttons.create').click()
        new = self.workspace['my-image']
        self.assertEqual(new.portal_type, 'Image')

    @unittest.skip('Broken IAppLayer test setup. Works when tested manually.')
    def test_add_content_image_with_imagefile(self):
        self.browser_login_as_site_administrator()
        self.browser.open('%s/@@add_content' % self.workspace.absolute_url())
        self.browser.getControl(name='portal_type').value = ['Image']
        self.browser.getControl(name='title').value = 'My Image'
        image_path = os.path.join(os.path.dirname(__file__), "plone_logo.png")
        image_ctl = self.browser.getControl(name='image')
        image_ctl.add_file(open(image_path), 'image/png', 'plone_logo.png')

        # XXX TODO
        # Submitting the form now fails with LocationError: (None, 'getSize')
        # ie. there's no image uploaded.
        # May have something to do with the checkbox for image not being set,
        # as demonstrated by writing the HTML into a file.
        handle = open('/tmp/test_add_content_image_with_imagefile.html', 'w+')
        handle.write(self.browser.contents)
        handle.close()

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
