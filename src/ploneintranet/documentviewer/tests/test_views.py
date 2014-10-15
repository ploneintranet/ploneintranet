# -*- coding: utf-8 -*-
import unittest
from plone import api
from ploneintranet.documentviewer.testing import \
    PLONEINTRANET_documentviewer_INTEGRATION_TESTING


class TestViews(unittest.TestCase):

    layer = PLONEINTRANET_documentviewer_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        import pdb;pdb.set_trace()

    def test_storage(self):
        '''
        '''
        view = api.content.get_view(
            'document_preview',
            self.portal,
            self.request,
        )
        view.thumbnail_storage

    def test_storage(self):
        '''
        '''
        view = api.content.get_view(
            'document_preview',
            self.portal,
            self.request,
        )
        view.thumbnail_storage
