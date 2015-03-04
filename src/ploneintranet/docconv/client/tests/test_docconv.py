from mock import Mock
from Testing.makerequest import makerequest
from plone import api
from plone.app.testing import setRoles
from plone.app.testing.interfaces import TEST_USER_ID
from plone.namedfile.file import NamedBlobFile
from zope import event
from zope.component import getAdapter
from zope.interface import alsoProvides
from zope.traversing.interfaces import BeforeTraverseEvent
import os

from ploneintranet.docconv.client.interfaces import IDocconv
from ploneintranet.docconv.client.interfaces import IPloneintranetDocconvClientLayer
from ploneintranet.docconv.client.adapters import DocconvAdapter
from ploneintranet.docconv.client.fetcher import BasePreviewFetcher
from ploneintranet.docconv.client.fetcher import fetchPreviews
from ploneintranet.docconv.client.testing import IntegrationTestCase


class TestDocconvLocal(IntegrationTestCase):
    """Test the docconv integration with local conversion"""

    def setUp(self):
        """ """
        portal = makerequest(self.layer['portal'])
        self.request = portal.REQUEST
        alsoProvides(self.request, IPloneintranetDocconvClientLayer)
        setRoles(portal, TEST_USER_ID, ('Manager',))

        # temporarily disable event handler so that we can test objects without
        # previews
        from ploneintranet.docconv.client import handlers
        _update_preview_images = handlers._update_preview_images
        handlers._update_preview_images = lambda obj, event: None

        self.workspace = api.content.create(
            type='Folder',
            title=u"Docconv Workspace",
            container=portal)
        ff = open(os.path.join(os.path.dirname(__file__), 'test.odt'), 'r')
        filedata = ff.read()
        ff.close()
        self.testfile = api.content.create(
            type='File',
            id='test-file',
            title=u"Test File",
            file=NamedBlobFile(data=filedata, filename=u'test.odt'),
            container=self.workspace)

        handlers._update_preview_images = _update_preview_images

        event.notify(BeforeTraverseEvent(portal, portal.REQUEST))

    def tearDown(self):
        api.content.delete(self.testfile)
        api.content.delete(self.workspace)

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
