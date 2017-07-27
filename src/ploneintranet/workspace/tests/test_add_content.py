# -*- coding: utf-8 -*-
from DateTime import DateTime
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

    def test_add_event_round_date(self):
        view = api.content.get_view(
            'add_event',
            self.portal,
            self.request,
        )

        self.assertEqual(
            view.round_date(DateTime('2000/01/01 00:00:00 GMT+2')),
            DateTime('2000/01/01 00:00:00 GMT+2')
        )
        self.assertEqual(
            view.round_date(DateTime('2000/01/01 00:15:00 GMT+2')),
            DateTime('2000/01/01 00:15:00 GMT+2')
        )
        self.assertEqual(
            view.round_date(DateTime('2000/01/01 00:15:01 GMT+2')),
            DateTime('2000/01/01 00:30:00 GMT+2')
        )

    def test_add_event_default_dates(self):
        view = api.content.get_view(
            'add_event',
            self.portal,
            self.request.clone(),
        )
        # if we do not request any date, the date will be today,
        # the time will be 9:00 AM
        # The code should take care of the current timezone
        self.assertEqual(view.default_datetime.hour(), 9)
        self.assertEqual(view.default_datetime, view.default_start)
        self.assertEqual(view.default_end.hour(), 10)

        # if we pass a date it will be used to setup the defaults
        view.request.set('date', '2000/01/01')
        view.request.__annotations__.pop('plone.memoize')
        self.assertEqual(view.default_end.year(), 2000)
        self.assertEqual(view.default_end.hour(), 10)
        self.assertEqual(view.default_end.minute(), 0)

        # if we pass a date ant a time it will be used to setup the defaults
        view.request.set('date', '2000/01/01T08:30')
        view.request.__annotations__.pop('plone.memoize')
        self.assertEqual(view.default_start.hour(), 8)
        self.assertEqual(view.default_start.minute(), 30)
        self.assertEqual(view.default_end.hour(), 9)
        self.assertEqual(view.default_end.minute(), 0)
