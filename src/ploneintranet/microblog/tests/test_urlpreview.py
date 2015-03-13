# -*- coding: utf-8 -*-
from ..interfaces import IURLPreview
from ..testing import PLONEINTRANET_MICROBLOG_INTEGRATION_TESTING
from pkg_resources import resource_filename
from test_statusupdate import StatusUpdate
from urllib import urlopen
import mock
import unittest2 as unittest


def request_get(url, timeout=0):
    '''Fetch a stream from local files.
    We don't need the full request.get stuff,
    we just want to open a local test file:
    urlopen is more than enough.

    See: http://stackoverflow.com/questions/10123929/python-requests-fetch-a-file-from-a-local-url  # noqa
    '''
    class FakeResponse(object):
        ''' This is a fake response
        '''
        def __init__(self, url):
            self.content = urlopen(url).read()

    return FakeResponse(url)


class URLPreviewTestCase(unittest.TestCase):

    layer = PLONEINTRANET_MICROBLOG_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    @mock.patch('requests.get', request_get)
    def test_simple_site(self):
        su = StatusUpdate('foo bar')
        url = 'file://%s' % resource_filename(
            'ploneintranet.microblog',
            'tests/data/simple_site.html'
        )
        previews = IURLPreview(su).generate_preview(url)
        self.assertEqual(previews[0], 'https://plone.org/logo@2x.png')

    @mock.patch('requests.get', request_get)
    def test_with_og_support(self):
        su = StatusUpdate('foo bar')
        url = 'file://%s' % resource_filename(
            'ploneintranet.microblog',
            'tests/data/og_support.html'
        )
        ogurl = 'http://content.plone.com/plone/social/test.jpg'
        previews = IURLPreview(su).generate_preview(url)
        self.assertEqual(previews[0], ogurl)
