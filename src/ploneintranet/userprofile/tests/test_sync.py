"""
The following tests use ZODBMutablePropertyProvider ('mutable_properties)
as a example foreign property provider.
"""
from datetime import datetime
from plone import api
from ploneintranet import api as pi_api
from ploneintranet.userprofile.tests.base import BaseTestCase
from ploneintranet.userprofile.sync import IUserProfileManager
from ploneintranet.userprofile.sync import AllUsersPropertySync


class SyncBaseTestCase(BaseTestCase):

    def _create_userprofiles(self):
        user = api.content.create(
            container=self.profiles,
            type='ploneintranet.userprofile.userprofile',
            id='johndoe',
            username='johndoe',
            first_name=u'John',
            last_name=u'Doe',
            email='johndoe@example.com',
            password='secret',
            confirm_password='secret',
        )
        return user

    def _check_set_last_sync(self, context):
        self.assertIsInstance(context.last_sync, datetime)

    def _set_foreign_property(self, member, key, value):
        acl_users = api.portal.get_tool(name='acl_users')
        plugin = acl_users['mutable_properties']
        sheet = plugin.getPropertiesForUser(member)
        sheet.setProperty(member, key, value)


class TestUserPropertyManager(SyncBaseTestCase):

    def test_sync(self):
        self.login_as_portal_owner()
        user = self._create_userprofiles()
        member = api.user.get(username=user.username)
        email = 'test@foo.com'
        self._set_foreign_property(member, 'email', email)

        user = pi_api.userprofile.get(user.username)
        IUserProfileManager(user).sync()
        self.assertEqual(user.email, email)
        catalog = api.portal.get_tool(name='portal_catalog')
        brains = catalog.searchResults(portal_type=user.portal_type)
        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0]['email'], email)
        self._check_set_last_sync(brains[0].getObject())


class TestAllUsersPropertySync(SyncBaseTestCase):

    def test__call__(self):
        self.login_as_portal_owner()
        self._create_userprofiles()
        view = AllUsersPropertySync(self.profiles, self.request)
        view()
        self._check_set_last_sync(self.profiles)
