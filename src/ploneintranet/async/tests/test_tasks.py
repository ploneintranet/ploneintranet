import transaction
import unittest

from plone import api
from ploneintranet.async import tasks

from ploneintranet.async.testing import FunctionalTestCase


class TestTasks(FunctionalTestCase):
    """Extra task tests, separate from the async framework tests."""

    @unittest.skip("This is just a skel. Please complete me.")
    def test_preview(self):
        """Verify async preview generation"""
        if not self.redis_running():
            self.fail("requires redis")
            return

        # FIXME: set up a test file
        context = self.portal.whatever.testfile
        generator = tasks.GeneratePreview(context, self.request)
        result = generator()
        self.waitfor(result)
        # we need to commit in order to see the other transaction
        transaction.commit()

        # now go and check that the preview has been generated
        self.assertTrue("Some check on context")

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
