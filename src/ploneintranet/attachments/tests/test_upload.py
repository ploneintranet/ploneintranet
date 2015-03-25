# -*- coding: utf-8 -*-
from pkg_resources import resource_string
from plone import api
from plone.app.blob.iterators import BlobStreamIterator
from plone.app.contenttypes.tests.test_image import dummy_image
from plone.namedfile.file import NamedBlobFile
from ploneintranet.attachments.testing import IntegrationTestCase
from ploneintranet.attachments.interfaces import IPloneintranetAttachmentsLayer
from ploneintranet.docconv.client.interfaces import (
    IPloneintranetDocconvClientLayer
)
from zope.interface import alsoProvides


class TestUpload(IntegrationTestCase):
    ''' Test that the upload view is functional
    '''
    def setUp(self):
        ''' define some helper variables here
        '''
        self.portal = self.layer['portal']
        self.request = self.layer['request'].clone()
        alsoProvides(self.request, IPloneintranetAttachmentsLayer)
        alsoProvides(self.request, IPloneintranetDocconvClientLayer)

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
        ''' Given an attachment we should have the urls to see its thumbnails
        '''
        upload_view = api.content.get_view(
            'upload-attachments',
            self.portal,
            self.request,
        )
        # Test objects that have no preview
        self.assertListEqual(
            upload_view.get_thumbs_urls(self.portal),
            [],
        )

        # Test objects that have a docconv generated preview
        self.assertListEqual(
            upload_view.get_thumbs_urls(self.pdf),
            ['http://nohost/plone/test-file/docconv_image_thumb.jpg?page=1']
        )

        # Test image previews
        urls = upload_view.get_thumbs_urls(self.image)
        self.assertTrue(len(urls) == 1)
        self.assertRegexpMatches(
            urls[0],
            'http://nohost/plone/test-image/@@images/(.*).jpeg'
        )

        # Test a File instance that contains an image
        urls = upload_view.get_thumbs_urls(self.fileimage)
        self.assertTrue(len(urls) == 1)
        self.assertRegexpMatches(
            urls[0],
            'http://nohost/plone/test-image-file/@@images/(.*).jpeg'
        )
        self.assertListEqual(
            upload_view.get_thumbs_urls(self.empty),
            []
        )

    def test_docconv_url_traversable(self):
        ''' In the previous test we returned a URL similar to this:
         - http://nohost/plone/test-file/docconv_image_thumb.jpg?page=1
        in the case of a docconv generated URL

        This test will protect the method that generates the urls
        from changes in the docconv module
        '''
        request = self.request.clone()
        request['page'] = 1
        view = api.content.get_view(
            'docconv_image_thumb.jpg',
            self.pdf,
            request,
        )
        self.assertIsInstance(view(), BlobStreamIterator)
