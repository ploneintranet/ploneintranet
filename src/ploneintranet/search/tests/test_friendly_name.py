from Products.CMFCore.interfaces import IIndexableObject
from plone import api
from plone.namedfile import NamedBlobFile
from zope.component import queryMultiAdapter

from ..testing import IntegrationTestCase


class TestFriendlyName(IntegrationTestCase):
    """ Test the friendly type name generator """

    def setUp(self):
        self.portal = api.portal.get()
        self.catalog = api.portal.get_tool(name='portal_catalog')
        self.doc1 = api.content.create(
            type='Document',
            title='Test Doc',
            container=self.portal,
        )
        self.file1 = api.content.create(
            type='File',
            title='Test File',
            container=self.portal,
            file=NamedBlobFile(
                data='blah blah',
                filename=u'test-file.pdf',
                contentType='application/pdf',
            )
        )

    def test_default_type(self):
        wrapped = queryMultiAdapter(
            (self.doc1, self.catalog),
            IIndexableObject)
        self.assertEqual(wrapped.friendly_type_name, 'Page')

    def test_file_type(self):
        wrapped = queryMultiAdapter(
            (self.file1, self.catalog),
            IIndexableObject)
        self.assertEqual(wrapped.friendly_type_name, 'PDF document')
