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
        self.su1 = pi_api.microblog.statusupdate.create(
            'foo',
        )
        self.su2 = pi_api.microblog.statusupdate.create(
            'bar', content_context=self.doc1,
        )
        self.su3 = pi_api.microblog.statusupdate.create(
            'baz', content_context=self.doc2, tags=['barx', ],
        )
        self.su4 = pi_api.microblog.statusupdate.create(
            'boo', content_context=self.doc2,
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
