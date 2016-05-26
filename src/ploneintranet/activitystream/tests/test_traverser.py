# -*- coding: utf-8 -*-
import unittest2 as unittest
from AccessControl import Unauthorized
from plone.app.testing import (
    setRoles, TEST_USER_ID, TEST_USER_NAME, TEST_USER_PASSWORD)
from plone.testing.z2 import Browser
from zope.component import queryUtility

from ploneintranet.activitystream.testing import (
    PLONEINTRANET_ACTIVITYSTREAM_FUNCTIONAL_TESTING
)
from ploneintranet.microblog.interfaces import IMicroblogTool
from ploneintranet.microblog.statusupdate import StatusUpdate


class TestStatusupdateTraverser(unittest.TestCase):

    layer = PLONEINTRANET_ACTIVITYSTREAM_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.container = queryUtility(IMicroblogTool)
        self.su = StatusUpdate('foo bar')
        self.container.add(self.su)
        self.baseurl = "{}/statusupdate/{}/".format(
            self.portal.absolute_url(), self.su.id
        )

        setRoles(self.portal, TEST_USER_ID, ['Member'])
        # Commit so that the test browser sees these changes
        import transaction
        transaction.commit()

        self.browser = Browser(self.app)
        self.browser.handleErrors = False
        self.browser.addHeader('Authorization', 'Basic %s:%s' % (
            TEST_USER_NAME, TEST_USER_PASSWORD,))

    def test_anon(self):
        browser = Browser(self.app)  # don't re-use self.browser
        url = self.baseurl + "post-menu.html"
        browser.open(url)
        # catches Unauthorized by redirecting to login form
        self.assertIn('Forgot your password', browser.contents)

    def test_post_menu(self):
        url = self.baseurl + "post-menu.html"
        self.browser.open(url)
        self.assertTrue('panel-edit-post.html' in self.browser.contents)

    def test_nosuch_id(self):
        url = "{}/statusupdate/12345/post-menu.html".format(
            self.portal.absolute_url()
        )
        with self.assertRaises(KeyError):
            self.browser.open(url)

    def test_disallowed_view(self):
        url = self.baseurl + "absolute_url"
        with self.assertRaises(Unauthorized):
            self.browser.open(url)
