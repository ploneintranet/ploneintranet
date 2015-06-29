# -*- coding: utf-8 -*-
from ZPublisher.Iterators import filestream_iterator
from plone import api
from plone.app.contenttypes.tests.test_image import dummy_image
from plone.namedfile.file import NamedBlobFile
from zope.interface import alsoProvides

from pkg_resources import resource_string
from ploneintranet.attachments.testing import IntegrationTestCase
from ploneintranet.attachments.interfaces import IPloneintranetAttachmentsLayer
from ploneintranet import api as pi_api


class TestUpload(IntegrationTestCase):
    """ Test that the upload view is functional
    """

    def setUp(self):
        """ define some helper variables here
        """
        self.portal = self.layer['portal']
        self.request = self.layer['request'].clone()
        alsoProvides(self.request, IPloneintranetAttachmentsLayer)

        # Docconv: will generate previews for this
        self.pdf = api.content.create(
            container=self.portal,
            type='File',
            id='test-file',
            file=NamedBlobFile(
                data=resource_string(
                    'ploneintranet.attachments.tests',
                    'plone.pdf'
                ).decode(
                    'latin1',
                    'utf8'
                ),
                filename=u'plone.pdf'
            ),
        )
        # This will be skipped by docconv: no need for preview generation
        self.image = api.content.create(
            container=self.portal,
            type='Image',
            id='test-image',
            image=dummy_image(),
        )
        # We also need a file that contains an image :)
        # This will be also skipped by docconv
        self.fileimage = api.content.create(
            container=self.portal,
            type='File',
            id='test-image-file',
            file=dummy_image(),
        )
        # We finally try with an empty file
        # This will be also skipped by docconv
        self.empty = api.content.create(
            container=self.portal,
            type='File',
            id='test-empty',
        )

    def test_get_thumbs_urls(self):
        """ Given an attachment we should have the urls to see its thumbnails
        """
        # Test objects that have a docconv generated preview
        self.assertEqual(
            pi_api.previews.get_thumbnail_url(self.pdf),
            'http://nohost/plone/test-file/@@thumbnail'
        )

        # Test image previews
        urls = pi_api.previews.get_preview_urls(self.image)
        self.assertTrue(len(urls) == 1)
        self.assertEqual(
            urls[0],
            'http://nohost/plone/test-image/@@preview?page=1&scale=preview'
        )

        # Test a File instance that contains an image
        urls = pi_api.previews.get_preview_urls(self.fileimage)
        self.assertTrue(len(urls) == 1)
        self.assertEqual(
            urls[0],
            'http://nohost/plone/test-image-file/@@preview?page=1&scale='
            'preview'
        )
        self.assertListEqual(
            pi_api.previews.get_preview_urls(self.empty),
            [pi_api.previews.fallback_image_url()]
        )

    def test_docconv_url_traversable(self):
        """ In the previous test we returned a URL similar to this:
         - http://nohost/plone/test-file/docconv_image_thumb.jpg?page=1
        in the case of a docconv generated URL

        This test will protect the method that generates the urls
        from changes in the docconv module
        """
        request = self.request.clone()
        request['page'] = 1
        view = api.content.get_view(
            'thumbnail',
            self.pdf,
            request,
        )
        self.assertIsInstance(view(), filestream_iterator)
