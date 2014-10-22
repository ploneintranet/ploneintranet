# -*- coding: utf-8 -*-
import unittest
from plone import api
from ploneintranet.documentviewer.testing import \
    PLONEINTRANET_documentviewer_INTEGRATION_TESTING
from zope.publisher.interfaces import NotFound
import os


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
                image=open(os.path.join(os.path.dirname(__file__), 'test.png')),  # noqa
            )
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

    def test_storage(self):
        '''
        '''
        self.assertEqual(self.image_view.thumbnail_storage, {})

    def test_get_default_preview_url(self):
        '''
        '''

        self.assertEqual(
            self.image_view.get_default_preview_url(),
            'http://nohost/plone/png.png'
        )
        self.assertEqual(
            self.portal_view.get_default_preview_url(),
            'http://nohost/plone/document.png'
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
            'http://nohost/plone/document.png'
        )

    def test_get_preview_image(self):
        ''' We should get a default preview
        '''
        preview = self.image_view.get_preview_image()
        self.assertEqual(
            self.request.response.headers,
            {
                'content-length': '19963',
                'content-type': 'image/png',
                'content-disposition': 'attachment;filename=test.png'
            }
        )
        self.assertTrue(preview.startswith('\x89PNG'))

    def test_traversable(self):
        ''' We should traverse to the view methods
        '''
        self.assertEqual(
            self.image.restrictedTraverse('@@document_preview/get_preview_url')(),  # noqa
            'http://nohost/plone/test_image/@@document_preview/get_preview_image'  # noqa
        )
        self.assertEqual(
            self.portal.restrictedTraverse('@@document_preview/get_preview_url')(),  # noqa
            'http://nohost/plone/document.png'
        )
        self.assertTrue(
            self.image.restrictedTraverse(
                '@@document_preview/get_preview_image'
            )().startswith('\x89PNG')
        )
        self.assertRaises(
            NotFound,
            self.portal.restrictedTraverse(
                '@@document_preview/get_preview_image'
            )
        )
