
# -*- coding: utf-8 -*-
from plone import api
from plone.dexterity.browser.view import DefaultView
from ploneintranet.layout.interfaces import INoBarcelonetaLayer
from ploneintranet.userprofile.browser.userprofilecontainer import View
from ploneintranet.userprofile.testing import PLONEINTRANET_USERPROFILE_FUNCTIONAL_TESTING  # noqa
from ploneintranet.userprofile.tests.base import BaseTestCase
from zope.interface import noLongerProvides


TEST_AVATAR_FILENAME = u'test_avatar.jpg'


class TestViews(BaseTestCase):

    layer = PLONEINTRANET_USERPROFILE_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestViews, self).setUp()
        self.login_as_portal_owner()

    def test_profiles_view(self):
        ''' Check the default view for the profile container redirects
        the user when we are using Quaive, but not when we are on the CMS
        '''
        view = api.content.get_view(
            'view',
            self.profiles,
            self.request.clone(),
        )
        self.assertIsInstance(view, View)

        # We redirect the user to the Plone site
        self.assertEqual(view(), 'http://nohost/plone/@@dashboard.html')

        # Now we fake a request from the CMS
        request = self.request.clone()
        noLongerProvides(request, INoBarcelonetaLayer)
        view = api.content.get_view(
            'view',
            self.profiles,
            request
        )
        # When this happens the dexterity default view is used
        self.assertIsInstance(view, DefaultView)
