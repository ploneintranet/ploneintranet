import transaction
import unittest

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

        # FIXME: use a 'normal' user
        self.basic_auth()  # set up basic authentication on self.request

        # FIXME: set up a test file
        context = self.portal.whatever.testfile
        generator = tasks.GeneratePreview(context, self.request)
        result = generator()
        self.waitfor(result)
        # we need to commit in order to see the other transaction
        transaction.commit()

        # now go and check that the preview has been generated
        self.assertTrue("Some check on context")
