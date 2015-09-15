# -*- coding: utf-8 -*-
from pkg_resources import resource_string
from plone import api
from plone.app.contenttypes.tests.test_image import dummy_image
from plone.namedfile.file import NamedBlobFile
from ploneintranet.attachments.testing import IntegrationTestCase
from ploneintranet.attachments.interfaces import IPloneintranetAttachmentsLayer
from ploneintranet import api as pi_api
from zope.interface import alsoProvides
from ZODB.blob import Blob


class TestUpload(IntegrationTestCase):
    ''' Test that the upload view is functional
    '''
    def setUp(self):
        ''' define some helper variables here
        '''
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
            upload_view.fallback_thumbs_urls,
        )

        # Test objects that have a generated preview
        self.assertTrue(
            '/test-file/small' in upload_view.get_thumbs_urls(self.pdf)[0]
        )

        # Test image previews
        urls = upload_view.get_thumbs_urls(self.image)
        self.assertTrue(len(urls) == 1)
        self.assertTrue('test-image/small' in urls[0])

        # Test a File instance that contains an image
        urls = upload_view.get_thumbs_urls(self.fileimage)
        self.assertTrue(len(urls) == 1)
        self.assertTrue('test-image-file/small' in urls[0])

        self.assertListEqual(
            upload_view.get_thumbs_urls(self.empty),
            upload_view.fallback_thumbs_urls
        )

    def test_previews_url_traversable(self):
        ''' In the previous test we returned a URL similar to this:
         - http://nohost/plone/@@dvpdfview/1/f/1fe3402718445/normal/dump_1.gif
        in the case of a c.dv generated URL

        This test will protect the method that generates the urls
        from changes in the ploneintranet api module
        '''
        request = self.request.clone()
        request['page'] = 1
        previews = pi_api.previews.get(self.pdf)
        self.assertIsInstance(previews[0], Blob)
