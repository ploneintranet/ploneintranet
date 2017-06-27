# -*- coding=utf-8 -*-
import os
import unittest
from DateTime import DateTime
from zope.interface import directlyProvides
from zope.component import queryUtility

from plone import api
from ploneintranet.microblog.browser.extract import ExtractAttachments
from ploneintranet.microblog.testing import \
    PLONEINTRANET_MICROBLOG_INTEGRATION_TESTING

from ploneintranet.microblog.interfaces import IMicroblogContext
from ploneintranet.microblog.interfaces import IMicroblogTool
from ploneintranet.microblog import statusupdate


class StatusUpdate(statusupdate.StatusUpdate):

    """Override actual implementation with unittest features"""

    def __init__(self, text, userid='dude',
                 microblog_context=None, content_context=None):
        self.userid = userid
        self.creator = userid
        super(StatusUpdate, self).__init__(
            text,
            microblog_context=microblog_context,
            content_context=content_context)

    def _init_userid(self):
        pass

    def _init_creator(self):
        pass

    def _init_microblog_context(self, thread_id,
                                microblog_context=None, content_context=None):
        self._m_context = microblog_context
        self._microblog_context_uuid = self._context2uuid(microblog_context)

    def _init_content_context(self, thread_id, content_context):
        self._c_context = content_context
        self._content_context_uuid = self._context2uuid(content_context)

    @property
    def microblog_context(self):
        return self._m_context

    @property
    def content_context(self):
        return self._c_context


class ExtractAttachmentsTestCase(unittest.TestCase):

    layer = PLONEINTRANET_MICROBLOG_INTEGRATION_TESTING

    odt_name = u'bärtige_flößer.odt'
    simple_odt_name = 'bartige_flosser.odt'
    png_name = u'vision-to-product.png'

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.portal.REQUEST
        self.portal_workflow = api.portal.get_tool('portal_workflow')
        self.mock_workspace1 = api.content.create(
            self.portal, 'Folder', 'workspace1')
        directlyProvides(self.mock_workspace1, IMicroblogContext)
        self.mock_workspace1.reindexObject()
        self.mock_workspace2 = api.content.create(
            self.portal, 'Folder', 'workspace2')
        directlyProvides(self.mock_workspace2, IMicroblogContext)
        self.mock_workspace2.reindexObject()
        # this needs to happen AFTER the directlyProvides, dunno why
        self.mock_folder = api.content.create(self.mock_workspace2,
                                              'Folder', 'my-folder')
        self.statuscontainer = queryUtility(IMicroblogTool)
        self.view = ExtractAttachments(self.portal, self.request)
        # provide the default user for tests
        api.user.create('dude@example.org', 'dude')

    def file_data(self, filename):
        path = os.path.join(os.path.dirname(__file__),
                            "uploads", filename)
        with open(path, 'rb') as fh:
            data = fh.read()
        return data

    @property
    def odt_data(self):
        return self.file_data(self.odt_name)

    @property
    def png_data(self):
        return self.file_data(self.png_name)

    def test_view_call(self):
        result = self.view()
        self.assertEquals('Extracted 0 attachments.', result)

    def test_get_statusupdates_sitewide(self):
        su1 = StatusUpdate('A', microblog_context=self.mock_workspace1)
        su2 = StatusUpdate('B')
        su3 = StatusUpdate('C', microblog_context=self.mock_workspace2)
        self.statuscontainer.add(su1)
        self.statuscontainer.add(su2)
        self.statuscontainer.add(su3)
        self.assertEquals(
            [su3, su1],
            [x for x in self.view.get_statusupdates()])

    def test_get_statusupdates_workspace(self):
        su1 = StatusUpdate('A', microblog_context=self.mock_workspace1)
        su2 = StatusUpdate('B')
        su3 = StatusUpdate('C', microblog_context=self.mock_workspace2)
        self.statuscontainer.add(su1)
        self.statuscontainer.add(su2)
        self.statuscontainer.add(su3)
        view = ExtractAttachments(self.mock_workspace1, self.request)
        self.assertEquals(
            [su1],
            [x for x in view.get_statusupdates()])

    def test_extract_attachment_png(self):
        su = StatusUpdate('A', microblog_context=self.mock_workspace1)
        su.add_attachment(self.png_name, self.png_data)
        self.statuscontainer.add(su)
        num_attachments = self.view.extract()
        self.assertEquals(1, num_attachments)
        # the original stream attachment is removed
        self.assertEquals([], [x for x in su.attachments.keys()])

    def test_extract_attachment_odt(self):
        su = StatusUpdate('A', microblog_context=self.mock_workspace1)
        su.add_attachment(self.odt_name, self.odt_data)
        self.statuscontainer.add(su)
        num_attachments = self.view.extract()
        self.assertEquals(1, num_attachments)
        # the original stream attachment is removed
        self.assertEquals([], [x for x in su.attachments.keys()])

    def test_extract_ignores_global_statusupdate(self):
        su = StatusUpdate('A')
        su.add_attachment(self.odt_name, self.odt_data)
        self.statuscontainer.add(su)
        num_attachments = self.view.extract()
        self.assertEquals(0, num_attachments)

    def test_extract_ignores_statusupdate_without_attachment(self):
        su = StatusUpdate('A', microblog_context=self.mock_workspace1)
        self.statuscontainer.add(su)
        num_attachments = self.view.extract()
        self.assertEquals(0, num_attachments)

    def test_extract_ignores_content_updates(self):
        su = StatusUpdate('A', microblog_context=self.mock_workspace1,
                          content_context=self.mock_folder)
        su.add_attachment(self.odt_name, self.odt_data)
        self.statuscontainer.add(su)
        num_attachments = self.view.extract()
        self.assertEquals(0, num_attachments)

    def test_extraction_creates_incoming_folder(self):
        su = StatusUpdate('A', microblog_context=self.mock_workspace1)
        su.add_attachment(self.odt_name, self.odt_data)
        self.statuscontainer.add(su)
        num_attachments = self.view.extract()
        self.assertEquals(1, num_attachments)
        self.assertIn(u'INCOMING', self.mock_workspace1)

    def test_extraction_creates_incoming_file(self):
        su = StatusUpdate('A', microblog_context=self.mock_workspace1)
        su.add_attachment(self.odt_name, self.odt_data)
        self.statuscontainer.add(su)
        num_attachments = self.view.extract()
        self.assertEquals(1, num_attachments)
        self.assertIn(u'INCOMING', self.mock_workspace1)
        self.assertIn(self.simple_odt_name, self.mock_workspace1.INCOMING)
        content = self.mock_workspace1.INCOMING[self.simple_odt_name]
        self.assertEquals(self.odt_name, content.file.filename)
        self.assertEquals(self.odt_data, content.file.data)

    def test_extraction_creates_incoming_image(self):
        su = StatusUpdate('A', microblog_context=self.mock_workspace1)
        su.add_attachment(self.png_name, self.png_data)
        self.statuscontainer.add(su)
        num_attachments = self.view.extract()
        self.assertEquals(1, num_attachments)
        self.assertIn(u'INCOMING', self.mock_workspace1)
        self.assertIn(self.png_name, self.mock_workspace1.INCOMING)
        content = self.mock_workspace1.INCOMING[self.png_name]
        self.assertEquals(self.png_name, content.image.filename)
        self.assertEquals(self.png_data, content.image.data)

    def test_extraction_content_context(self):
        su = StatusUpdate('A', microblog_context=self.mock_workspace1)
        su.add_attachment(self.odt_name, self.odt_data)
        self.statuscontainer.add(su)
        self.view.extract()
        content = self.mock_workspace1.INCOMING[self.simple_odt_name]
        self.assertEquals(content, su.content_context)

    def test_extraction_content_context_indexed(self):
        su = StatusUpdate('A', microblog_context=self.mock_workspace1)
        su.add_attachment(self.odt_name, self.odt_data)
        self.statuscontainer.add(su)
        self.view.extract()
        content = self.mock_workspace1.INCOMING[self.simple_odt_name]
        self.assertEquals(
            [su],
            [x for x in self.statuscontainer.content_values(content)])

    def test_extraction_metadata_title(self):
        su = StatusUpdate('A', microblog_context=self.mock_workspace1)
        su.add_attachment(self.odt_name, self.odt_data)
        self.statuscontainer.add(su)
        self.view.extract()
        content = self.mock_workspace1.INCOMING[self.simple_odt_name]
        self.assertEquals(self.odt_name, content.title)

    def test_extraction_metadata_creator(self):
        api.user.create('killroy@example.org', 'killroy')
        su = StatusUpdate('A', microblog_context=self.mock_workspace1,
                          userid='killroy')
        su.add_attachment(self.odt_name, self.odt_data)
        self.statuscontainer.add(su)
        self.view.extract()
        content = self.mock_workspace1.INCOMING[self.simple_odt_name]
        self.assertEquals(('killroy',), content.creators)

    def test_extraction_metadata_created(self):
        su = StatusUpdate('A', microblog_context=self.mock_workspace1)
        su.add_attachment(self.odt_name, self.odt_data)
        su.date = DateTime(2015, 01, 01)
        self.statuscontainer.add(su)
        self.view.extract()
        content = self.mock_workspace1.INCOMING[self.simple_odt_name]
        self.assertEquals(su.date, content.created())

    def test_extraction_metadata_owner(self):
        killroy = api.user.create('killroy@example.org', 'killroy')
        su = StatusUpdate('A', microblog_context=self.mock_workspace1,
                          userid='killroy')
        su.add_attachment(self.odt_name, self.odt_data)
        self.statuscontainer.add(su)
        self.view.extract()
        content = self.mock_workspace1.INCOMING[self.simple_odt_name]
        self.assertEquals('killroy', content.getOwner().getId())
        self.assertIn('Owner', api.user.get_roles(username='killroy',
                                                  obj=content))
        self.assertIn('Owner', api.user.get_roles(user=killroy, obj=content))
