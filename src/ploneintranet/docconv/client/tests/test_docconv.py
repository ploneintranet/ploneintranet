from mock import Mock
from mock import patch
from Testing.makerequest import makerequest
from Products.ATContentTypes.content.file import ATFile
from collective.documentviewer.settings import GlobalSettings
from plone import api
from plone.app.testing import setRoles
from plone.app.testing.interfaces import TEST_USER_ID
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.file import NamedBlobImage
from tempfile import mkdtemp
from zope import event
from zope.component import getAdapter
from zope.interface import alsoProvides
from zope.traversing.interfaces import BeforeTraverseEvent
import os
import shutil

from ploneintranet.docconv.client.interfaces import IDocconv
from ploneintranet.docconv.client.interfaces import \
    IPloneintranetDocconvClientLayer
from ploneintranet.docconv.client.adapters import DocconvAdapter
from ploneintranet.docconv.client.fetcher import BasePreviewFetcher
from ploneintranet.docconv.client.fetcher import fetchPreviews
from ploneintranet.docconv.client.testing import IntegrationTestCase

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
        _update_preview_images = handlers._update_preview_images
        handlers._update_preview_images = lambda obj, event: None

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

        handlers._update_preview_images = _update_preview_images

        event.notify(BeforeTraverseEvent(portal, portal.REQUEST))

    def tearDown(self):
        api.content.delete(self.testfile)
        api.content.delete(self.workspace)
        shutil.rmtree(self.storage_dir)

    def test_getPayload(self):
        # We don't actually allow archetypes in a workspace
        # but we need to check that this method supports them
        # so we manually set one up here
        testfile_at = ATFile(TEST_FILENAME)
        testfile_at.initializeArchetype()
        testfile_at.setFile(self.filedata,
                            filename=TEST_FILENAME)
        fetcher = BasePreviewFetcher(testfile_at)
        mimetype, data = fetcher.getPayload()
        self.assertEqual(mimetype, TEST_MIME_TYPE)
        self.assertEqual(data, self.filedata,
                         'File data does not match')

        # ... and then for default dexterity
        fetcher = BasePreviewFetcher(self.testfile)
        mimetype, data = fetcher.getPayload()
        self.assertEqual(mimetype, TEST_MIME_TYPE)
        self.assertEqual(data, self.filedata,
                         'File data does not match')

    def test_docconv_adapter_on_new_object(self):
        docconv = IDocconv(self.testfile)
        self.assertFalse(docconv.has_pdf())
        self.assertFalse(docconv.has_previews())
        self.assertFalse(docconv.has_thumbs())
        self.assertEquals(docconv.get_pdf(), None)
        self.assertEquals(docconv.get_previews(), None)
        self.assertEquals(docconv.get_thumbs(), None)

    def test_named_docconv_adapter(self):
        alt_docconv = getAdapter(
            self.testfile, IDocconv, name='plone.app.async')
        self.assertTrue(isinstance(alt_docconv, DocconvAdapter))

    def test_document(self):
        testdoc = api.content.create(
            type='Document',
            id='test-doc',
            title=u"Test Document",
            text=u'The main text',
            container=self.workspace)
        fetchPreviews(testdoc,
                      virtual_url_parts=['dummy', ],
                      vr_path='/plone')
        docconv = IDocconv(testdoc)
        self.assertTrue(docconv.has_pdf())
        self.assertTrue(docconv.has_previews())
        self.assertTrue(docconv.has_thumbs())

    def test_empty_document_skipped(self):
        testdoc = api.content.create(
            type='Document',
            id='test-doc',
            title=u"Test Document",
            container=self.workspace)
        with patch.object(BasePreviewFetcher, '__call__') as mock_call:
            fetchPreviews(testdoc,
                          virtual_url_parts=['dummy', ],
                          vr_path='/plone')
            self.assertFalse(mock_call.called)

    def _test_image_skipped(self, convert_method_name):
        imagedata = (
            'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00\xff\xff'
            '\xff,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
        testdoc = api.content.create(
            type='Image',
            id='test-image',
            title=u"Test Image",
            image=NamedBlobImage(data=imagedata, filename=u'testimage.gif'),
            container=self.workspace)
        with patch.object(
                BasePreviewFetcher, convert_method_name) as mock_convert:
            fetchPreviews(testdoc,
                          virtual_url_parts=['dummy', ],
                          vr_path='/plone')
            self.assertFalse(mock_convert.called)

    def test_image_skipped(self):
        self._test_image_skipped('convert_locally')

    def test_fetch_docconv_data(self):
        fetchPreviews(self.testfile,
                      virtual_url_parts=['dummy', ],
                      vr_path='/plone')
        docconv = IDocconv(self.testfile)
        self.assertTrue(docconv.has_pdf())
        self.assertTrue(docconv.has_previews())
        self.assertTrue(docconv.has_thumbs())

    def test_docconv_image_views(self):
        preview_view = self.testfile.restrictedTraverse(
            'docconv_image_preview.jpg')
        self.assertFalse(preview_view.available())
        self.assertEquals(preview_view.pages_count(), 0)
        preview_img = preview_view()
        self.assertEquals(preview_view.request.RESPONSE.getStatus(), 404)
        self.assertIs(preview_img, None)

        fetchPreviews(self.testfile,
                      virtual_url_parts=['dummy', ],
                      vr_path='/plone')

        for view_name in ['docconv_image_preview.jpg',
                          'docconv_image_thumb.jpg']:
            self.request.RESPONSE.setStatus(200)
            preview_view = self.testfile.restrictedTraverse(view_name)
            self.assertTrue(preview_view.available())
            self.assertEquals(preview_view.pages_count(), 1)
            preview_img = preview_view()
            self.assertIsNot(preview_img, None)
            self.assertNotEquals(preview_view.request.RESPONSE.getStatus(),
                                 404)

    def test_docconv_pdf_views(self):
        pdf_view = self.testfile.restrictedTraverse(
            'pdf')
        pdf_data = pdf_view()
        self.assertEquals(pdf_view.request.RESPONSE.getStatus(), 302)
        self.assertIn('pdf-not-available', pdf_data)

        # mock our way around the async call
        fetch_call = lambda: fetchPreviews(
            self.testfile,
            virtual_url_parts=['dummy', ],
            vr_path='/plone')
        DocconvAdapter.generate_all = Mock(
            return_value=True,
            side_effect=fetch_call)

        self.request.RESPONSE.setStatus(200)
        self.request['ACTUAL_URL'] = (
            self.testfile.absolute_url() + '/request-pdf')
        pdf_request_view = self.testfile.restrictedTraverse(
            'request-pdf')
        pdf_data = pdf_request_view()
        DocconvAdapter.generate_all.assert_called_with()
        self.assertIn('requested', pdf_data)
        self.assertEquals(pdf_request_view.request.RESPONSE.getStatus(), 200)

        self.request.RESPONSE.setStatus(200)
        pdf_view = self.testfile.restrictedTraverse(
            'pdf')
        pdf_data = pdf_view()
        self.assertIsNotNone(pdf_data)
        self.assertNotIn('not generated yet', pdf_data)
        self.assertEquals(pdf_view.request.RESPONSE.getStatus(), 200)

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


class TestDocconvRemote(TestDocconvLocal):
    """Test the docconv integration with the remote call"""

    def setUp(self):
        """ """
        def mock_convert_on_server(self, payload, datatype):
            test_zip = os.path.join(os.path.split(__file__)[0],
                                    'Test_Document.zip')
            zipfile = open(test_zip, 'r')
            data = zipfile.read()
            data = self.unpack_zipdata(data)
            zipfile.close()
            return data
        self._convert_on_server = BasePreviewFetcher.convert_on_server
        BasePreviewFetcher.convert_on_server = mock_convert_on_server

        super(TestDocconvRemote, self).setUp()

    def tearDown(self):
        super(TestDocconvRemote, self).tearDown()
        BasePreviewFetcher.convert_on_server = self._convert_on_server

    def test_image_skipped(self):
        self._test_image_skipped('convert_on_server')
