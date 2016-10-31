# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import login
from plone.app.testing.interfaces import SITE_OWNER_NAME
from plone.app.textfield.value import RichTextValue
from ploneintranet.docconv.client.testing import FunctionalTestCase
from ploneintranet.docconv.client.html_converter import HTMLConverter
from BeautifulSoup import BeautifulSoup
from plone.app.contenttypes.tests.test_image import dummy_image

import os


class TestHTMLToPDF(FunctionalTestCase):
    '''Test views for ploneintranet.docconv.client
    '''

    def setUp(self):
        '''Custom shared utility setup for tests.'''
        self.portal = self.layer['portal']
        login(self.portal.aq_parent, SITE_OWNER_NAME)
        self.document = api.content.create(
            self.portal,
            id='Doc1',
            type='Document',
        )

    def test_convert_virtual_url(self):
        converter = HTMLConverter(self.document)
        self.assertEquals(
            converter.convert_virtual_url('http://notplone/some.img'),
            'http://notplone/some.img',
        )
        self.assertEquals(
            converter.convert_virtual_url('http://nohost/plone/some.img'),
            '/plone/some.img',
        )
        self.document.REQUEST['VIRTUAL_URL_PARTS'] = (
            'http://quaive.com/',
            'quaive',
            'workspaces/w1/a-doc',
        )
        self.assertEquals(
            converter.convert_virtual_url('http://quaive.com/quaive/some.img'),
            '/plone/some.img',
        )

    def test_extract_images(self):
        converter = HTMLConverter(self.document)
        tmpdir = os.path.join(converter.storage_dir, 'images')
        os.mkdir(tmpdir)
        self.image = api.content.create(
            container=self.portal,
            type='Image',
            id='image.png',
            image=dummy_image(),
        )
        doc_html = '<body><img src="http://nohost/plone/image.png"/><body>'
        doc_soup = BeautifulSoup(doc_html)
        html = converter.extract_images(doc_soup, tmpdir)
        self.assertTrue('src="images/image0.png"' in str(html))
        self.assertTrue(os.path.exists(os.path.join(tmpdir, 'image0.png')))

    def test_run_conversion(self):
        raw_text = u'¯\_(ツ)_/¯<br/>'
        richtext = RichTextValue(
            raw=raw_text,
            mimeType='text/plain',
            outputMimeType='text/x-html-safe',
        )
        self.document.text = richtext
        converter = HTMLConverter(self.document)
        converter.run_conversion()
        pdf_path = os.path.join(converter.storage_dir, 'dump.pdf')
        self.assertTrue(os.path.exists(pdf_path))
