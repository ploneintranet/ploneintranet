from Testing.makerequest import makerequest
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

    def test_show_like(self):
        util = getUtility(ITodoUtility)
        userid = api.user.get_current().getId()
        toggle_view = api.content.get_view(
            'toggle_like',
            self.doc1,
            self.layer['request']
        )

        output = toggle_view()
        # TODO: improve
        self.assertIn('like_button', output)
        results = util.query(
            userid,
            LIKE,
            ignore_completed=False
        )
        self.assertEqual(len(results), 0)

    def test_toggle_like(self):
        util = getUtility(ITodoUtility)
        userid = api.user.get_current().getId()
        self.request.form['like_button'] = 'like'
        toggle_view = api.content.get_view(
            'toggle_like',
            self.doc1,
            self.request
        )

        # Toggle like for doc1
        output = toggle_view()
        self.assertIn('(1)', output)
        user_likes = util.query(
            userid,
            LIKE,
            ignore_completed=False
        )
        total_likes = util.query(
            verbs=LIKE,
            content_uids=self.doc1.UID(),
            ignore_completed=False
        )

        self.assertEqual(len(user_likes), 1)
        self.assertEqual(len(user_likes), len(total_likes))
        # Toggle like for doc1
        toggle_view()
        user_likes = util.query(
            userid,
            LIKE,
            ignore_completed=False
        )
        self.assertEqual(len(user_likes), 0)
