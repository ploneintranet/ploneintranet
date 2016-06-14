import unittest2 as unittest
from zope.interface import alsoProvides

from plone import api
from plone.app.testing import TEST_USER_ID, setRoles

from ploneintranet.microblog.interfaces import IMicroblogContext
from ploneintranet.microblog.statusupdate import StatusUpdate
from ploneintranet.microblog.testing import (
    PLONEINTRANET_MICROBLOG_CONTENTUPDATES_TESTING)


class TestDeleteSubscriber(unittest.TestCase):

    layer = PLONEINTRANET_MICROBLOG_CONTENTUPDATES_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.container = api.portal.get_tool('ploneintranet_microblog')
        self.ws_id = self.portal.invokeFactory('Folder', 'workspace')
        self.microblog_context = self.portal[self.ws_id]
        alsoProvides(self.microblog_context, IMicroblogContext)
        self.microblog_context.reindexObject()
        self.doc_id = self.microblog_context.invokeFactory('Document', 'mydoc')
        self.document = self.microblog_context[self.doc_id]
        self.document.reindexObject()

    def test_delete_content_context(self):
        su1 = StatusUpdate('test')
        self.container.add(su1)
        su2 = StatusUpdate('foobar', content_context=self.document)
        self.container.add(su2)
        self.microblog_context.manage_delObjects([self.doc_id])
        self.assertEqual([su1], (list(self.container.values())))

    def test_delete_microblog_context(self):
        su1 = StatusUpdate('test')
        self.container.add(su1)
        su2 = StatusUpdate('foobar', microblog_context=self.microblog_context)
        self.container.add(su2)
        self.portal.manage_delObjects([self.ws_id])
        self.assertEqual([su1], (list(self.container.values())))

    def test_delete_microblog_context_and_content(self):
        su1 = StatusUpdate('test', content_context=self.document)
        self.container.add(su1)
        su2 = StatusUpdate('foobar', microblog_context=self.microblog_context)
        self.container.add(su2)
        self.portal.manage_delObjects([self.ws_id])
        self.assertEqual([], (list(self.container.values())))

    def test_delete_content_replies(self):
        su1 = StatusUpdate('test', content_context=self.document)
        self.container.add(su1)
        su2 = StatusUpdate('foobar', thread_id=su1.id)
        self.container.add(su2)
        self.microblog_context.manage_delObjects([self.doc_id])
        self.assertEqual([], (list(self.container.values())))
