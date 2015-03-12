# -*- coding: utf-8 -*-
import unittest
from plone import api
from plone.app.blob.field import ImageField
from plone.app.contenttypes.tests.test_image import dummy_image
from ploneintranet.docconv.client.adapters import DocconvAdapter
from ploneintranet.docconv.client.config import THUMBNAIL_KEY
from ploneintranet.documentviewer.testing import (
    PLONEINTRANET_documentviewer_INTEGRATION_TESTING
)
from zope.annotation import IAnnotations
from zope.publisher.interfaces import NotFound


class TestViews(unittest.TestCase):

    layer = PLONEINTRANET_documentviewer_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        with api.env.adopt_roles(['Manager']):
            self.image = api.content.create(
                self.portal,
                'Image',
                'test_image',
                image=dummy_image(),
            )
            annotations = IAnnotations(self.image)
            thumbnail = ImageField()
            thumbnail.set(self.image, dummy_image().data)
            annotations[THUMBNAIL_KEY] = list([thumbnail])

        self.image_view = api.content.get_view(
            'document_preview',
            self.image,
            self.request,
        )
        self.portal_view = api.content.get_view(
            'document_preview',
            self.portal,
            self.request,
        )

    def test_docconv(self):
        ''' Get the IDocconv adapter
        '''
        self.assertIsInstance(self.image_view.docconv, DocconvAdapter)
        self.assertIsInstance(self.portal_view.docconv, DocconvAdapter)

    def test_get_default_preview_url(self):
        '''
        '''
        self.assertEqual(
            self.image_view.get_default_preview_url(),
            'http://nohost/plone/image.png'
        )
        self.assertEqual(
            self.portal_view.get_default_preview_url(),
            'http://nohost/plone/application.png'
        )

    def test_get_preview_url(self):
        ''' We should get a default preview
        '''
        self.assertEqual(
            self.image_view.get_preview_url(),
            'http://nohost/plone/test_image/@@document_preview/get_preview_image'  # noqa
        )
        self.assertEqual(
            self.portal_view.get_preview_url(),
            'http://nohost/plone/application.png'
        )

    def test_get_preview_image(self):
        ''' We should get a default preview
        '''
        self.assertEqual(
            self.image_view.get_preview_image(),
            'http://nohost/plone/test_image/docconv_image_thumb.jpg'
        )

    def test_traversable(self):
        ''' We should traverse to the view methods
        '''
        self.assertEqual(
            self.image.restrictedTraverse('@@document_preview/get_preview_url')(),  # noqa
            'http://nohost/plone/test_image/@@document_preview/get_preview_image'  # noqa
        )
        self.assertEqual(
            self.portal.restrictedTraverse('@@document_preview/get_preview_url')(),  # noqa
            'http://nohost/plone/application.png'
        )
        self.assertEqual(
            self.image.restrictedTraverse('@@document_preview/get_preview_image')(),  # noqa
            'http://nohost/plone/test_image/docconv_image_thumb.jpg'
        )
        self.assertRaises(
            NotFound,
            self.portal.restrictedTraverse(
                '@@document_preview/get_preview_image'
            )
        )
