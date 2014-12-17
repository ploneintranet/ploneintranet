from plone import api
from zope.component import getUtility

from ..interfaces import ITodoUtility, LIKE

from ..testing import IntegrationTestCase


class TestToggleLikeView(IntegrationTestCase):

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.doc1 = api.content.create(
            container=self.portal,
            type='Document',
            id='doc1',
            title='Doc 1'
        )

    def test_toggle_like(self):
        util = getUtility(ITodoUtility)
        userid = api.user.get_current().getId()
        toggle_view = api.content.get_view(
            'toggle_like',
            self.doc1,
            self.layer['request']
        )

        # Toggle like for doc1
        toggle_view()
        results = util.query(
            userid,
            LIKE,
            ignore_completed=False
        )
        self.assertEqual(len(results), 1)

        # Toggle like for doc1
        toggle_view()
        results = util.query(
            userid,
            LIKE,
            ignore_completed=False
        )
        self.assertEqual(len(results), 0)