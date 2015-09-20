import os
from plone import api
from plone.namedfile.file import NamedBlobFile
from ploneintranet.api.testing import FunctionalTestCase
from ploneintranet import api as pi_api
from ZODB.blob import Blob
from plone.resource.file import FilesystemFile

TEST_MIME_TYPE = 'application/vnd.oasis.opendocument.text'
TEST_FILENAME = u'test.odt'


class TestPreviews(FunctionalTestCase):

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.testfolder = api.content.create(
            type='Folder',
            title=u"Testfolder",
            container=self.portal)
        ff = open(os.path.join(os.path.dirname(__file__), TEST_FILENAME), 'r')
        self.filedata = ff.read()
        ff.close()
        self.testfile = api.content.create(
            type='File',
            id='test-file',
            title=u"Test File",
            file=NamedBlobFile(data=self.filedata, filename=TEST_FILENAME),
            container=self.testfolder)

        self.testdoc = api.content.create(
            type='Document',
            id='test-doc',
            title=u"Test Doc",
            text=u"This is a test doc with no preview generated (yet)",
            container=self.testfolder)

    def test_get(self):
        previews = pi_api.previews.get(self.testdoc)  # docs have no preview
        self.assertEqual(previews, [])

        previews = pi_api.previews.get(self.testfile)  # files do have one
        self.assertNotEqual(previews, [])
        self.assertEqual(len(previews), 1)

    def test_get_preview_urls(self):
        preview_urls = pi_api.previews.get_preview_urls(self.testfile)
        self.assertEqual(len(preview_urls), 1)
        self.assertTrue('/normal/dump_1' in preview_urls[0])
        self.assertTrue(self.testfile.UID() in preview_urls[0])

        preview_urls = pi_api.previews.get_preview_urls(self.testfile, 'small')
        self.assertTrue('/small/dump_1' in preview_urls[0])

        preview_urls = pi_api.previews.get_preview_urls(self.testfile, 'large')
        self.assertTrue('/large/dump_1' in preview_urls[0])

        preview_urls = pi_api.previews.get_preview_urls(self.testfile, 'foo')
        self.assertTrue('/large/dump_1' in preview_urls[0])

    def test_fallback_image_url(self):
        fallback = pi_api.previews.fallback_image_url(self.testfile)
        self.assertTrue(
            '++theme++ploneintranet.theme/generated/media/logos/plone-intranet-square.svg'  # noqa
            in fallback)

    def test_get_thumbnail(self):
        thumbnail = pi_api.previews.get_thumbnail(self.testfile)
        self.assertIsInstance(thumbnail, Blob)  # found a thumb

        thumbnail = pi_api.previews.get_thumbnail(self.testdoc)
        self.assertIsInstance(thumbnail, FilesystemFile)  # return default img
