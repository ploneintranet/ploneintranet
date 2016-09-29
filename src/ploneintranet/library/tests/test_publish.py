# coding=utf-8
from plone import api
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from ploneintranet.library.testing import IntegrationTestCase

from ploneintranet.library.behaviors.publish import IPublishWidely


class TestPublishWidely(IntegrationTestCase):

    def setUp(self):
        super(TestPublishWidely, self).setUp()
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ('Manager',))
        self.testsection = api.content.create(
            type='ploneintranet.library.section',
            title='Human Resources',
            container=self.portal.library)
        self.testfolder = api.content.create(
            type='ploneintranet.library.folder',
            title='Holidays',
            container=self.testsection)

    def test_behavior_active_document(self):
        content = api.content.create(
            type='Document',
            title='Holidays previous year',
            container=self.testfolder)
        self.assertTrue(IPublishWidely.providedBy(content))

    def test_behavior_active_file(self):
        content = api.content.create(
            type='File',
            title='Holidays previous year file',
            container=self.testfolder)
        self.assertTrue(IPublishWidely.providedBy(content))

    def test_behavior_active_image(self):
        content = api.content.create(
            type='Image',
            title='Holidays previous year image',
            container=self.testfolder)
        self.assertTrue(IPublishWidely.providedBy(content))

    def test_behavior_active_link(self):
        content = api.content.create(
            type='Link',
            title='Holidays previous year link',
            container=self.testfolder)
        self.assertTrue(IPublishWidely.providedBy(content))
