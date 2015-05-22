# -*- coding: utf-8 -*-
from zope.component import getUtility

from plone import api as plone_api

from ploneintranet import api as pi_api
from ploneintranet.network.interfaces import INetworkTool
from ploneintranet.network.testing import IntegrationTestCase
from ploneintranet.network.testing import set_browserlayer


class TestToggleFollowView(IntegrationTestCase):

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        set_browserlayer(self.request)
        self.util = getUtility(INetworkTool)

    def test_toggle_follow(self):
        pi_api.userprofile.create(
            username='johndoe',
            email='johndoe@doe.com',
            approve=True,
        )
        janedoe = pi_api.userprofile.create(
            username='janedoe',
            email='janedoe@doe.com',
            approve=True,
        )

        self.assertNotIn('johndoe', self.util.get_followers('user', 'janedoe'))
        self.assertNotIn('janedoe', self.util.get_following('user', 'johndoe'))
        self.login('johndoe')
        view = plone_api.content.get_view(
            'toggle_follow', janedoe, self.request)
        view()
        self.assertIn('johndoe', self.util.get_followers('user', 'janedoe'))
        self.assertIn('janedoe', self.util.get_following('user', 'johndoe'))
        view()
        self.assertNotIn('johndoe', self.util.get_followers('user', 'janedoe'))
        self.assertNotIn('janedoe', self.util.get_following('user', 'johndoe'))
