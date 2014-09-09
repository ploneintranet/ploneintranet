# -*- coding: utf-8 -*-
import unittest2 as unittest
from ..testing import PLONESOCIAL_MICROBLOG_INTEGRATION_TESTING
from ..interfaces import IURLPreview
from test_statusupdate import StatusUpdate


class URLPreviewTestCase(unittest.TestCase):

    layer = PLONESOCIAL_MICROBLOG_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_simple_site(self):
        su = StatusUpdate('foo bar')
        previews = IURLPreview(su).generate_preview('http://plone.org')
        self.assertEqual(previews[0], 'https://plone.org/logo@2x.png')

    def test_with_og_support(self):
        su = StatusUpdate('foo bar')
        ogurl = 'http://content6.flixster.com/movie/11/16/80/11168096_800.jpg'
        previews = IURLPreview(su).generate_preview(
            'http://www.rottentomatoes.com/m/matrix/')
        self.assertEqual(previews[0], ogurl)
