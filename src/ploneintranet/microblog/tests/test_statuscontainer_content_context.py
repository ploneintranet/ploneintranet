import unittest2 as unittest
from plone.app.testing import TEST_USER_ID, setRoles
from zope.component import queryUtility
from plone import api

from ploneintranet import api as pi_api
from ploneintranet.microblog.interfaces import IMicroblogTool
from ploneintranet.microblog.testing import \
    PLONEINTRANET_MICROBLOG_INTEGRATION_TESTING


class TestStatusContainerContentContext(unittest.TestCase):
    """NB these tests have the content subscribers disabled.
    This only tests the content reference indexing backend.
    """

    layer = PLONEINTRANET_MICROBLOG_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager', 'Member'])
        self.container = queryUtility(IMicroblogTool)
        self.doc1 = api.content.create(
            container=self.portal,
            type='Document',
            title='My document One',
        )
        self.doc2 = api.content.create(
            container=self.portal,
            type='Document',
            title='My document Two',
        )
        self.su1 = pi_api.microblog.statusupdate.create('')
        self.su2 = pi_api.microblog.statusupdate.create(
            '', content_context=self.doc1,
        )
        self.su3 = pi_api.microblog.statusupdate.create(
            '', content_context=self.doc2, tags=['barx', ],
        )
        self.su4 = pi_api.microblog.statusupdate.create(
            '', content_context=self.doc2,
        )

    def test_items_content(self):
        values = [x[1] for x in self.container.content_items(
            self.doc1)]
        self.assertEqual(1, len(values))
        self.assertEqual([self.su2], values)

    def test_values_content(self):
        values = list(self.container.content_values(
            self.doc2))
        # chronological order, not reversed
        self.assertEqual([self.su3, self.su4], values)

    # re-using this test fixture for human/content filters

    def test_is_human_items(self):
        values = [x[1] for x in self.container.is_human_items()]
        self.assertEqual(1, len(values))
        self.assertEqual([self.su1], values)

    def test_is_human_values(self):
        values = list(self.container.is_human_values())
        self.assertEqual(1, len(values))
        self.assertEqual([self.su1], values)

    def test_is_content_items(self):
        values = [x[1] for x in self.container.is_content_items()]
        self.assertEqual(3, len(values))
        self.assertEqual([self.su4, self.su3, self.su2], values)

    def test_is_content_values(self):
        values = list(self.container.is_content_values())
        self.assertEqual(3, len(values))
        self.assertEqual([self.su4, self.su3, self.su2], values)
