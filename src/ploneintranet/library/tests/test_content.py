from plone import api
from plone.app.testing import applyProfile
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from ploneintranet.library.testing import IntegrationTestCase


class TestContent(IntegrationTestCase):

    def setUp(self):
        super(TestContent, self).setUp()
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ('Manager',))

    def test_library_created(self):
        self.assertTrue('library' in self.portal)
        self.assertEqual('ploneintranet.library.app',
                         self.portal.library.portal_type)

    def test_library_created_once(self):
        self.assertTrue('library' in self.portal)
        api.content.rename(self.portal['library'], new_id='handbook')
        applyProfile(self.portal, 'ploneintranet.library:default')
        self.assertFalse('library' in self.portal)

    def test_section(self):
        ob = api.content.create(
            type='ploneintranet.library.section',
            title='Human Resources',
            container=self.portal.library)
        self.assertTrue(ob in self.portal.library.objectValues())

    def test_sections_not_nested(self):
        ob = api.content.create(
            type='ploneintranet.library.section',
            title='Human Resources',
            container=self.portal.library)
        with self.assertRaises(api.exc.InvalidParameterError):
            api.content.create(
                type='ploneintranet.library.section',
                title='Human Resources 2',
                container=ob)

    def test_folder_not_toplevel(self):
        with self.assertRaises(api.exc.InvalidParameterError):
            api.content.create(
                type='ploneintranet.library.folder',
                title='a folder',
                container=self.portal.library)

    def test_folder(self):
        ob1 = api.content.create(
            type='ploneintranet.library.section',
            title='Human Resources',
            container=self.portal.library)
        ob2 = api.content.create(
            type='ploneintranet.library.folder',
            title='Holidays',
            container=ob1)
        self.assertTrue(ob2 in ob1.objectValues())

    def test_page(self):
        ob1 = api.content.create(
            type='ploneintranet.library.section',
            title='Human Resources',
            container=self.portal.library)
        ob2 = api.content.create(
            type='ploneintranet.library.folder',
            title='Holidays',
            container=ob1)
        ob3 = api.content.create(
            type='Document',
            title='Holidays previous year',
            container=ob2)
        self.assertTrue(ob3 in ob2.objectValues())

    def test_tree(self):
        ob1 = api.content.create(
            type='ploneintranet.library.section',
            title='Human Resources',
            container=self.portal.library)
        ob2 = api.content.create(
            type='ploneintranet.library.folder',
            title='Leave Policies',
            container=ob1)
        ob3 = api.content.create(
            type='ploneintranet.library.folder',
            title='Holidays',
            container=ob2)
        ob4 = api.content.create(
            type='Document',
            title='Holidays previous year',
            container=ob3)
        self.assertTrue(ob4 in ob3.objectValues())
