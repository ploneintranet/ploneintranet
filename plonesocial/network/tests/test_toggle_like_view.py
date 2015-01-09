from Testing.makerequest import makerequest
from plone import api
from plonesocial.network.interfaces import ILikesContainer
from plonesocial.network.testing import FunctionalTestCase
from plonesocial.network.testing import IntegrationTestCase
from plonesocial.network.testing import set_browserlayer
from zope.component import getUtility
import unittest2 as unittest


class TestToggleLikeView(IntegrationTestCase):

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        set_browserlayer(self.request)
        self.doc1 = api.content.create(
            container=self.portal,
            type='Document',
            id='doc1',
            title='Doc 1'
        )
        self.user_id = api.user.get_current().getId()

    def test_show_like(self):
        util = getUtility(ILikesContainer)
        view = api.content.get_view('toggle_like', self.portal, self.request)
        self.assertRaises(KeyError, view)
        item_id = api.content.get_uuid(self.doc1)
        view = view.publishTraverse(self.request, item_id)
        output = view()
        self.assertIn('like_button', output)
        self.assertIn(item_id, output)
        self.assertFalse(util.is_item_liked_by_user(self.user_id, item_id))

    def test_toggle_like(self):
        util = getUtility(ILikesContainer)
        self.request.form['like_button'] = 'like'
        view = api.content.get_view('toggle_like', self.portal, self.request)
        item_id = api.content.get_uuid(self.doc1)
        view = view.publishTraverse(self.request, item_id)

        # Toggle like for doc1
        output = view()
        self.assertIn('(1)', output)
        self.assertIn('Unlike', output)
        user_likes = util.get_items_for_user(self.user_id)

        self.assertTrue(util.is_item_liked_by_user(self.user_id, item_id))
        self.assertEqual(len(user_likes), 1)

        # Toggle like for doc1
        output = view()
        user_likes = util.get_items_for_user(self.user_id)
        self.assertEqual(len(user_likes), 0)
        self.assertIn('(0)', output)
        self.assertIn('Like', output)
