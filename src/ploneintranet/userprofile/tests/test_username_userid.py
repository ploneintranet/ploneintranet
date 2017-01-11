# -*- coding: utf-8 -*-
from zExceptions.unauthorized import Unauthorized
from Products.membrane.interfaces import IMembraneUserObject
from dexterity.membrane.behavior.settings import IDexterityMembraneSettings
from plone import api
from plone.app.testing import logout
from plone.app.testing.interfaces import SITE_OWNER_NAME
from plone.testing import z2

from ploneintranet.userprofile.testing import \
    PLONEINTRANET_USERPROFILE_BROWSER_TESTING
from ploneintranet.userprofile.testing import \
    PLONEINTRANET_USERPROFILE_FUNCTIONAL_TESTING

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


class TestUserAPI(unittest.TestCase):
    """Document the membrane versus acl_users API results"""

    layer = PLONEINTRANET_USERPROFILE_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.portal.REQUEST
        self.membrane_tool = api.portal.get_tool('membrane_tool')
        self.profiles = self.portal.profiles
        self.setup_profiles()

    def setup_profiles(self):
        z2.login(self.app['acl_users'], SITE_OWNER_NAME)
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
        self.member1 = api.user.get(userid=self.userid1)
        self.member2 = api.user.get_current()

    def test_membrane_id(self):
        self.assertEquals(self.profile1.id, self.userid1)

    def test_membrane_getId(self):
        self.assertEquals(self.profile1.getId(), self.userid1)

    def test_membrane_getUserId(self):
        with self.assertRaises(AttributeError):
            self.profile1.getUserId()
        adapted = IMembraneUserObject(self.profile1)
        self.assertEquals(adapted.getUserId(), self.userid1)

    def test_membrane_username(self):
        self.assertEquals(self.profile1.username, self.userid1)

    def test_membrane_getUserName(self):
        with self.assertRaises(AttributeError):
            self.profile1.getUserName()
        adapted = IMembraneUserObject(self.profile1)
        self.assertEquals(adapted.getUserName(), self.userid1)

    def test_member_id(self):
        self.assertEquals(self.member1.id, self.userid1)
        self.assertEquals(self.member2.id, SITE_OWNER_NAME)

    def test_member_getId(self):
        self.assertEquals(self.member1.getId(), self.userid1)
        self.assertEquals(self.member2.getId(), SITE_OWNER_NAME)

    def test_member_getUserId(self):
        """
        Members backed by a membrane object have getUserId().
        Pure acl users have not.
        """
        self.assertEquals(self.member1.getUserId(), self.userid1)
        with self.assertRaises(AttributeError):
            self.member2.getUserId()

    def test_member_username(self):
        with self.assertRaises(AttributeError):
            self.member1.username
        with self.assertRaises(AttributeError):
            self.member2.username

    def test_member_getUserName(self):
        self.assertEquals(self.member1.getUserName(), self.userid1)
        self.assertEquals(self.member2.getUserName(), SITE_OWNER_NAME)

    def test_membrane_edit_username_id_accessors(self):
        self.profile1.username = 'new_username'
        self.assertEquals(self.profiles.objectIds(), [self.userid1])
        self.assertEquals(self.profile1.getId(), self.userid1)
        adapted = IMembraneUserObject(self.profile1)
        self.assertEquals(adapted.getUserId(), self.userid1)
        members = api.user.get_users(groupname='Members')
        self.assertEquals([x.getId() for x in members], [self.userid1])

    @unittest.expectedFailure
    def test_membrane_move_id_accessors(self):
        """Moving membrane profiles will not work"""
        newid = 'my_new_vanity_url'
        # just reassigning the id is not enough, have to actually move it
        api.content.move(self.profile1, id=newid)
        self.assertEquals(self.profiles.objectIds(), [newid])
        self.assertEquals(self.profile1.getId(), newid)
        adapted = IMembraneUserObject(self.profile1)
        self.assertEquals(adapted.getUserId(), newid)
        # with or without reindex, this ultimately fails
        self.profile1.reindexObject()
        members = api.user.get_users(groupname='Members')
        self.assertEquals([x.getId() for x in members], [newid])  # FAILS


class TestUserAPIEmail(TestUserAPI):
    """Performs all the same tests via inheritance, but now in
    a use_email_as_username scenario.

    Differences are documented by test method overrides below.
    """

    def setUp(self):
        # Set config before user creation.
        # If you do it afterward, you need to reindex the users
        self.use_email_as_username()
        super(TestUserAPIEmail, self).setUp()

    def use_email_as_username(self):
        api.portal.set_registry_record('use_email_as_username', True,
                                       IDexterityMembraneSettings)
        commit()

    def test_membrane_getUserName(self):
        with self.assertRaises(AttributeError):
            self.profile1.getUserName()
        adapted = IMembraneUserObject(self.profile1)
        self.assertEquals(adapted.getUserName(), self.email1)

    def test_member_getUserName(self):
        self.assertEquals(self.member1.getUserName(), self.email1)
        self.assertEquals(self.member2.getUserName(), SITE_OWNER_NAME)
