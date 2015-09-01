from Products.CMFCore.interfaces import IIndexableObject
from plone import api
from plone.namedfile import NamedBlobFile
from zope.component import queryMultiAdapter
import transaction

from .. import testing


class TestFriendlyName(testing.IntegrationTestCase):
    """Test the friendly type name generator."""

    def setUp(self):
        super(TestFriendlyName, self).setUp()
        self.portal = api.portal.get()
        self.catalog = api.portal.get_tool(name='portal_catalog')
        self.doc1 = self._create_content(
            type='Document',
            title='Test Doc',
            container=self.portal,
        )
        self.file1 = self._create_content(
            type='File',
            title='Test File',
            container=self.portal,
            file=NamedBlobFile(
                data='blah blah',
                filename=u'test-file.pdf',
                contentType='application/pdf',
            )
        )
        transaction.commit()

    def test_default_type(self):
        iobj = queryMultiAdapter((self.doc1, self.catalog), IIndexableObject)
        self.assertEqual(iobj.friendly_type_name, 'Page')

    def test_file_type(self):
        iobj = queryMultiAdapter((self.file1, self.catalog), IIndexableObject)
        self.assertEqual(iobj.friendly_type_name, 'PDF document')
