# -*- coding: utf-8 -*-
from pkg_resources import resource_string
from subprocess import CalledProcessError
from mock import patch
from zope.interface import alsoProvides
from zope.component import getMultiAdapter
from zope.component import createObject
from zope.component import queryUtility
from plone import api
from plone.dexterity.interfaces import IDexterityFTI
from plone.namedfile.file import NamedBlobFile
from ploneintranet.attachments.attachments import IAttachmentStorage
from ploneintranet.attachments.attachments import IAttachmentStoragable
from ploneintranet.attachments.interfaces import IPloneintranetAttachmentsLayer

from ..browser.docconv import _parse_cmd_output
from ..testing import IntegrationTestCase


class TestDocconv(IntegrationTestCase):
    """
    Tests for the docconv browser view
    """

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test__parse_cmd_output(self):
        cmd = ['uname', '-a']
        parsed = _parse_cmd_output(cmd)
        self.assertIsInstance(parsed, list)

        cmd = ['not-a-command']
        with self.assertRaises(OSError):
            _parse_cmd_output(cmd)

        cmd = ['ps', '-quux']
        with self.assertRaises(CalledProcessError):
            _parse_cmd_output(cmd)

    @patch('ploneintranet.async.browser.docconv._parse_cmd_output')
    def test_previews(self, _parse_cmd_output):
        _parse_cmd_output.return_value = ''
        doc = api.content.create(
            container=self.portal,
            type='Document',
            id='test-document',
            title=u'Test document'
        )
        alsoProvides(self.request, IPloneintranetAttachmentsLayer)
        alsoProvides(doc, IAttachmentStoragable)
        attachments = IAttachmentStorage(doc)
        file_fti = queryUtility(IDexterityFTI, name='File')
        file_ = createObject(
            file_fti.factory,
            id='test-file',
            file=NamedBlobFile(
                data=resource_string(
                    'ploneintranet.async.tests',
                    'plone.docx'
                ).decode(
                    'latin1',
                    'utf8'
                ),
                filename=u'plone.docx'
            )
        )
        attachments.add(file_)
        previews_view = getMultiAdapter(
            (file_, self.request),
            name='generate-previews'
        )
        previews_view()
        self.assertTrue(_parse_cmd_output.called)
        self.assertEqual(_parse_cmd_output.call_count, 1)
        args, kwargs = _parse_cmd_output.call_args
        self.assertRegexpMatches(args[0][0], r'^.*\/docsplit$')
        self.assertEqual(
            [i for i in args[0][1:] if isinstance(i, basestring)],
            ['images',
             '--size',
             '180,700,1000',
             '--format',
             'png',
             '--rolling',
             '--output',
             '--pages',
             '1-20']
        )
        self.assertEqual(kwargs, {})
