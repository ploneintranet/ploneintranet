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

        self.image = api.content.create(
            container=self.portal,
            type='Image',
            id='test-image',
            image=dummy_image(),
        )
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

    def test_get_thumbs_urls(self):
        ''' Given an attachment we should have the urls to see its thumbnails
        '''
        upload_view = api.content.get_view(
            'upload-attachments',
            self.portal,
            self.request,
        )
        self.assertListEqual(
            upload_view.get_thumbs_urls(self.portal),
            [],
        )
        self.assertListEqual(
            upload_view.get_thumbs_urls(self.pdf),
            ['http://nohost/plone/test-file/docconv_image_thumb.jpg?page=1']
        )
        self.assertListEqual(
            upload_view.get_thumbs_urls(self.image),
            []
        )

    def test_url_traversable(self):
        ''' In the previous test we returned this URL

        I don't want anybody to break it!
        '''
        request = self.request.clone()
        request['page']=1
        view = api.content.get_view(
            'docconv_image_thumb.jpg',
            self.pdf,
            request,
        )

        self.assertIsInstance(view(), BlobStreamIterator)
