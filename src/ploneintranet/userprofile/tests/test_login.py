# -*- coding: utf-8 -*-
from zExceptions.unauthorized import Unauthorized
from dexterity.membrane.behavior.settings import IDexterityMembraneSettings
from plone import api
from plone.app.testing import logout
from plone.app.testing.interfaces import SITE_OWNER_NAME
from plone.testing import z2

from ploneintranet.userprofile.testing import \
    PLONEINTRANET_USERPROFILE_BROWSER_TESTING

from transaction import commit
import unittest


class TestLoginBase(unittest.TestCase):

    layer = PLONEINTRANET_USERPROFILE_BROWSER_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.portal.REQUEST
        self.membrane_tool = api.portal.get_tool('membrane_tool')
        self.profiles = self.portal.profiles
        self.setup_profiles()
        commit()  # make setup visible to ZServer thread
        self.browser = z2.Browser(self.app)
        self.browser.handleErrors = False

    def setup_profiles(self):
        self.admin_login()
        self.userid1 = 'john@example.id'
        self.email1 = 'john@example.name'
        self.profile1 = api.content.create(
            container=self.profiles,
            type='ploneintranet.userprofile.userprofile',
            id=self.userid1,
            username=self.userid1,
            email=self.email1,
            first_name='John',
            last_name='Doe',
            password='secret',
            confirm_password='secret',
        )
        api.content.transition(self.profile1, 'approve')
        self.profile1.reindexObject()

        self.userid2 = 'jane@example.org'
        self.email2 = 'jane@example.org'
        self.profile2 = api.content.create(
            container=self.profiles,
            type='ploneintranet.userprofile.userprofile',
            id=self.userid2,
            username=self.userid2,
            email=self.email2,
            first_name='Jane',
            last_name='Doe',
            password='secret',
            confirm_password='secret',
        )
        api.content.transition(self.profile2, 'approve')
        self.profile2.reindexObject()

        self.admin_logout()

    def browser_login(self, username, password='secret'):
        """
        helper method to login as specific user

        :param username: the username of the user to add to the group
        :type username: str
        :rtype: None

        """
        self.browser.open(self.portal.absolute_url() + '/login')
        self.browser.getControl(name='__ac_name').value = username
        self.browser.getControl(name='__ac_password').value = password
        self.browser.getControl(name='submit').click()
        return 'You are now logged in' in self.browser.contents

    def browser_is_loggedin(self, userid=''):
        """An extra http roundtrip to verify cookie is properly set"""
        try:
            self.browser.open(self.portal.absolute_url())
        except Unauthorized:
            return False
        return userid in self.browser.contents

    def admin_login(self):
        """
        helper method to login as site admin
        """
        z2.login(self.app['acl_users'], SITE_OWNER_NAME)

    def admin_logout(self):
        """
        helper method to logout site admin
        """
        logout()


class TestLoginUserid(TestLoginBase):
    """Test logging in on userid"""

    def test_login_userid(self):
        loggedin = self.browser_login(self.userid1)
        self.assertTrue(loggedin)
        self.assertTrue(self.browser_is_loggedin(self.userid1))

    def test_membrane_settings_email(self):
        self.assertFalse(api.portal.get_registry_record(
            'use_email_as_username', IDexterityMembraneSettings))

    def test_login_userid_invalid(self):
        loggedin = self.browser_login('smith')
        self.assertFalse(loggedin)
        self.assertFalse(self.browser_is_loggedin('smith'))

    def test_setup_Members(self):
        members = api.user.get_users(groupname='Members')
        self.assertEqual(sorted([x.id for x in members]),
                         [self.userid2, self.userid1])


class TestLoginEmail(TestLoginBase):
    """Test logging in on email.
    """

    def setUp(self):
        # Set config before user creation.
        # If you do it afterward, you need to reindex the users
        self.use_email_as_username()
        super(TestLoginEmail, self).setUp()

    def use_email_as_username(self):
        api.portal.set_registry_record('use_email_as_username', True,
                                       IDexterityMembraneSettings)
        commit()

    def test_membrane_settings_email(self):
        self.assertTrue(api.portal.get_registry_record(
            'use_email_as_username', IDexterityMembraneSettings))

    def test_setup_id(self):
        self.assertEqual(self.profile1.id, self.userid1)

    def test_setup_username(self):
        self.assertEqual(self.profile1.username, self.userid1)

    def test_setup_Members(self):
        members = api.user.get_users(groupname='Members')
        self.assertEqual(sorted([x.id for x in members]),
                         [self.userid2, self.userid1])

    def test_login_email_matches_userid(self):
        loggedin = self.browser_login(self.userid2)  # == email2
        self.assertTrue(loggedin)
        self.assertTrue(self.browser_is_loggedin(self.userid2))

    def test_login_email_different_userid(self):
        loggedin = self.browser_login(self.userid1)
        self.assertFalse(loggedin)

    def test_login_email_different_email(self):
        loggedin = self.browser_login(self.email1)
        self.assertTrue(loggedin)
        self.assertTrue(self.browser_is_loggedin(self.userid1))
