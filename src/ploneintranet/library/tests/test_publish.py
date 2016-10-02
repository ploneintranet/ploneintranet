# coding=utf-8
from plone import api
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from zope.interface.verify import verifyObject

from ploneintranet.library.testing import IntegrationTestCase
from ploneintranet.library.behaviors.publish import IPublishWidely


class TestPublishWidely(IntegrationTestCase):

    def setUp(self):
        super(TestPublishWidely, self).setUp()
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ('Manager',))
        self.source_folder = api.content.create(
            type='Folder',
            title='Source folder',
            container=self.portal)
        self.source_document = api.content.create(
            type='Document',
            title='Holidays previous year',
            container=self.source_folder)
        api.content.transition(self.source_document, 'publish')
        self.library_section = api.content.create(
            type='ploneintranet.library.section',
            title='Human Resources',
            container=self.portal.library)
        self.library_folder = api.content.create(
            type='ploneintranet.library.folder',
            title='Holidays',
            container=self.library_section)
        setRoles(self.portal, TEST_USER_ID, ('Reviewer', 'Contributor'))

    def test_behavior_interface(self):
        adapted = IPublishWidely(self.source_document)
        self.assertTrue(verifyObject(IPublishWidely, adapted))

    def test_behavior_active_document(self):
        content = self.source_document
        self.assertFalse(IPublishWidely.providedBy(content))
        adapted = IPublishWidely(content)
        self.assertTrue(IPublishWidely.providedBy(adapted))

    def test_behavior_active_file(self):
        content = api.content.create(
            type='File',
            title='Holidays previous year file',
            container=self.source_folder)
        self.assertFalse(IPublishWidely.providedBy(content))
        adapted = IPublishWidely(content)
        self.assertTrue(IPublishWidely.providedBy(adapted))

    def test_behavior_active_image(self):
        content = api.content.create(
            type='Image',
            title='Holidays previous year image',
            container=self.source_folder)
        self.assertFalse(IPublishWidely.providedBy(content))
        adapted = IPublishWidely(content)
        self.assertTrue(IPublishWidely.providedBy(adapted))

    def test_behavior_active_link(self):
        content = api.content.create(
            type='Link',
            title='Holidays previous year link',
            container=self.source_folder)
        api.content.transition(content, 'publish')
        self.assertFalse(IPublishWidely.providedBy(content))
        adapted = IPublishWidely(content)
        self.assertTrue(IPublishWidely.providedBy(adapted))

    def test_permission(self):
        adapted = IPublishWidely(self.source_document)
        self.assertTrue(adapted.can_publish_widely())
        setRoles(self.portal, TEST_USER_ID, ('Member',))
        self.assertFalse(adapted.can_publish_widely())

    def test_workflow(self):
        adapted = IPublishWidely(self.source_document)
        self.assertTrue(adapted.can_publish_widely())
        api.content.transition(self.source_document, 'retract')
        self.assertFalse(adapted.can_publish_widely())

    def test_workflow_noworkflow(self):
        content = api.content.create(
            type='Image',
            title='Holidays previous year image',
            container=self.source_folder)
        adapted = IPublishWidely(content)
        self.assertTrue(adapted.can_publish_widely())

    def test_location(self):
        content = api.content.create(
            type='Document',
            title='Library document',
            container=self.library_folder)
        api.content.transition(content, 'publish')
        adapted = IPublishWidely(content)
        self.assertFalse(adapted.can_publish_widely())

    def test_copy_to_target(self):
        adapted = IPublishWidely(self.source_document)
        new = adapted.copy_to(self.library_section)  # invalid target
        self.assertEquals(None, new)

    def test_copy_to(self):
        adapted = IPublishWidely(self.source_document)
        new = adapted.copy_to(self.library_folder)
        self.assertIn(new, self.library_folder.objectValues())
        self.assertEquals(new.title, self.source_document.title)

    def test_relation_source(self):
        adapted = IPublishWidely(self.source_document)
        self.assertEquals(adapted.source(), None)
        new = adapted.copy_to(self.library_folder)
        new_adapted = IPublishWidely(new)
        self.assertEquals(new_adapted.source(), self.source_document)
        self.assertNotEquals(new_adapted.source(), None)

    def test_relation_target(self):
        adapted = IPublishWidely(self.source_document)
        self.assertEquals(adapted.target(), None)
        new = adapted.copy_to(self.library_folder)
        self.assertEquals(adapted.target(), new)
        self.assertNotEquals(adapted.target(), None)

    def test_publish_only_once(self):
        adapted = IPublishWidely(self.source_document)
        self.assertTrue(adapted.can_publish_widely())
        adapted.copy_to(self.library_folder)
        self.assertFalse(adapted.can_publish_widely())
