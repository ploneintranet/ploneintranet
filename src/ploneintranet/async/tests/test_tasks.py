import os
import transaction
import unittest

from plone import api
from plone.namedfile.file import NamedBlobFile

from ploneintranet import api as pi_api
from ploneintranet.async import tasks
from ploneintranet.async.testing import FunctionalTestCase

TEST_MIME_TYPE = 'application/vnd.oasis.opendocument.text'
TEST_FILENAME = u'test.odt'


class TestTasks(FunctionalTestCase):
    """Extra task tests, separate from the async framework tests."""

    @unittest.skip("This only works if ASYNC_ENABLED is True.")
    def test_preview(self):
        """Verify async preview generation"""
        if not self.redis_running():
            self.fail("requires redis")
            return

        ff = open(os.path.join(os.path.dirname(__file__), TEST_FILENAME), 'r')
        self.filedata = ff.read()
        ff.close()
        # Temporarily enable Async
        self.testfile = api.content.create(
            type='File',
            id='test-file',
            title=u"Test File",
            file=NamedBlobFile(data=self.filedata, filename=TEST_FILENAME),
            container=self.portal)

        context = getattr(self.portal, 'test-file')
        self.assertFalse(pi_api.previews.has_previews(context))

        generator = tasks.GeneratePreview(context, self.request)
        result = generator()
        self.waitfor(result, timeout=15.0)

        # we need to commit in order to see the other transaction
        # now go and check that the preview has been generated
        transaction.commit()
        self.assertTrue(pi_api.previews.has_previews(context))

    def test_reindex(self):
        """Verify object reindexing"""
        if not self.redis_running():
            self.fail("requires redis")
            return

        # set up a test page
        context = api.content.create(
            type='Document',
            title='Test Document',
            container=self.portal)
        # api.create auto-indexes. modification does not
        context.title = 'Foobar Document'
        # we need to commit to make the object visible for async
        transaction.commit()
        # verify that our change is not indexed yet
        catalog = api.portal.get_tool('portal_catalog')
        self.assertFalse(context.title in [x.Title for x in catalog()])

        result = tasks.ReindexObject(context, self.request)()
        self.waitfor(result)
        # we need to commit in order to see the other transaction
        transaction.commit()
        # check that our modification was indexed
        self.assertTrue(context.title in [x.Title for x in catalog()])
