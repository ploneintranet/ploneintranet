from plone import api
from ploneintranet.userprofile.interfaces import IMemberGroup
from ploneintranet.userprofile.tests.base import BaseTestCase
from zope.interface import directlyProvides


class TestMemberGroupAdapter(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)
        self.login_as_portal_owner()
        self.folder1 = api.content.create(
            self.portal, 'Folder', 'folder-1', 'Folder 1')
        self.folder2 = api.content.create(
            self.folder1, 'Folder', 'folder-2', 'Folder 2')
        self.page = api.content.create(
            self.folder2, 'Document', 'page', 'My Page')

    def test_portal(self):
        with self.assertRaises(TypeError):
            IMemberGroup(self.portal)

    def test_page_noadapter(self):
        with self.assertRaises(TypeError):
            IMemberGroup(self.page)

    def test_direct(self):
        directlyProvides(self.folder1, IMemberGroup)
        self.assertEquals(IMemberGroup(self.folder1), self.folder1)

    def test_indirect(self):
        directlyProvides(self.folder1, IMemberGroup)
        self.assertEquals(IMemberGroup(self.page), self.folder1)
