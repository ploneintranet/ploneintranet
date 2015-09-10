# from mock import Mock
from Testing.makerequest import makerequest
from collective.documentviewer.settings import GlobalSettings
from plone import api
from plone.app.testing import setRoles
from plone.app.testing.interfaces import TEST_USER_ID
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.file import NamedBlobImage
from tempfile import mkdtemp
from zope import event
from zope.interface import alsoProvides
from zope.traversing.interfaces import BeforeTraverseEvent
import os
import shutil

from ploneintranet.docconv.client.interfaces import IDocconv
from ploneintranet.docconv.client.interfaces import \
    IPloneintranetDocconvClientLayer
from ploneintranet.docconv.client.testing import IntegrationTestCase
from ploneintranet.docconv.client.handlers import handle_file_creation
from collective.documentviewer.settings import Settings

TEST_MIME_TYPE = 'application/vnd.oasis.opendocument.text'
TEST_FILENAME = u'test.odt'


class TestDocconvLocal(IntegrationTestCase):
    """Test the docconv integration with local conversion"""

    def setUp(self):
        """ """
        portal = makerequest(self.layer['portal'])
        self.request = portal.REQUEST
        alsoProvides(self.request, IPloneintranetDocconvClientLayer)
        setRoles(portal, TEST_USER_ID, ('Manager',))

        gsettings = GlobalSettings(portal)
        self.storage_dir = mkdtemp()
        gsettings.storage_location = self.storage_dir

        # temporarily disable event handler so that we can test objects without
        # previews
        from ploneintranet.docconv.client import handlers
        handle_file_creation = handlers.handle_file_creation
        handlers.handle_file_creation = lambda obj, event: None

        self.workspace = api.content.create(
            type='Folder',
            title=u"Docconv Workspace",
            container=portal)
        ff = open(os.path.join(os.path.dirname(__file__), TEST_FILENAME), 'r')
        self.filedata = ff.read()
        ff.close()
        self.testfile = api.content.create(
            type='File',
            id='test-file',
            title=u"Test File",
            file=NamedBlobFile(data=self.filedata, filename=TEST_FILENAME),
            container=self.workspace)

        handlers.handle_file_creation = handle_file_creation

        event.notify(BeforeTraverseEvent(portal, portal.REQUEST))

    def tearDown(self):
        api.content.delete(self.testfile)
        api.content.delete(self.workspace)
        shutil.rmtree(self.storage_dir)

    def test_convert_previews(self):
        settings = Settings(self.testfile)
        self.assertEqual(settings.successfully_converted, None)
        self.assertEqual(settings.num_pages, None)
        self.assertEqual(settings.blob_files, None)

        handle_file_creation(self.testfile)

        settings = Settings(self.testfile)
        self.assertEqual(settings.successfully_converted, True)
        self.assertEqual(settings.num_pages, 1)
        self.assertEqual(len(settings.blob_files), 3)

    def test_docconv_adapter_on_new_object(self):
        docconv = IDocconv(self.testfile)
        self.assertFalse(docconv.has_previews())
        self.assertFalse(docconv.has_thumbs())
        self.assertEquals(docconv.get_previews(), None)
        self.assertEquals(docconv.get_thumbs(), None)

    def _test_document(self):
        # Document. Conversion to PDF not yet supported
        testdoc = api.content.create(
            type='Document',
            id='test-doc',
            title=u"Test Document",
            text=u'The main text',
            container=self.workspace)
        handle_file_creation(testdoc)
        docconv = IDocconv(testdoc)
        self.assertTrue(docconv.has_previews())

    def test_image(self):
        imagedata = (
            'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00\xff\xff'
            '\xff,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
        testdoc = api.content.create(
            type='Image',
            id='test-image',
            title=u"Test Image",
            image=NamedBlobImage(data=imagedata, filename=u'testimage.gif'),
            container=self.workspace)
        handle_file_creation(testdoc)
        settings = Settings(testdoc)
        self.assertEquals(len(settings.blob_files), 3)

    def test_docconv_image_views(self):
        docconv = IDocconv(self.testfile)
        self.assertEquals(docconv.has_previews(), False)

        handle_file_creation(self.testfile)

        self.assertEquals(docconv.has_previews(), True)

    # def test_docconv_pdf_views(self):
    #     pdf_view = self.testfile.restrictedTraverse(
    #         'pdf')
    #     pdf_data = pdf_view()
    #     self.assertEquals(pdf_view.request.RESPONSE.getStatus(), 302)
    #     self.assertIn('pdf-not-available', pdf_data)

    #     # mock our way around the async call
    #     fetch_call = lambda: fetchPreviews(
    #         self.testfile,
    #         virtual_url_parts=['dummy', ],
    #         vr_path='/plone')
    #     DocconvAdapter.generate_all = Mock(
    #         return_value=True,
    #         side_effect=fetch_call)

    #     self.request.RESPONSE.setStatus(200)
    #     self.request['ACTUAL_URL'] = (
    #         self.testfile.absolute_url() + '/request-pdf')
    #     pdf_request_view = self.testfile.restrictedTraverse(
    #         'request-pdf')
    #     pdf_data = pdf_request_view()
    #     DocconvAdapter.generate_all.assert_called_with()
    #     self.assertIn('requested', pdf_data)
    #     self.assertEquals(pdf_request_view.request.RESPONSE.getStatus(), 200)

    #     self.request.RESPONSE.setStatus(200)
    #     pdf_view = self.testfile.restrictedTraverse(
    #         'pdf')
    #     pdf_data = pdf_view()
    #     self.assertIsNotNone(pdf_data)
    #     self.assertNotIn('not generated yet', pdf_data)
    #     self.assertEquals(pdf_view.request.RESPONSE.getStatus(), 200)

    def test_event_handler(self):
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ('Manager',))
        fileob = api.content.create(
            type='File',
            title=u"Test File",
            file=NamedBlobFile(data=self.filedata, filename=TEST_FILENAME),
            container=self.workspace)
        docconv = IDocconv(fileob)
        self.assertTrue(docconv.has_previews())
