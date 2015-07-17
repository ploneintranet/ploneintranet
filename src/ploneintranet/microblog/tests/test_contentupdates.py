import unittest
from plone import api
from ploneintranet.microblog.testing import\
    PLONEINTRANET_MICROBLOG_INTEGRATION_TESTING


class TestContentStatusUpdate(unittest.TestCase):

    layer = PLONEINTRANET_MICROBLOG_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_content_status_update(self):
        doc = api.content.create(
            container=self.portal,
            type='Document',
            title='My document',
        )
        api.content.transition(doc, to_state='published')

        # Need a way to look up the status update that
        # was created!!
