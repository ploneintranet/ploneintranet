"""
The following tests use a mock PAS properties plugin.

Re-uses the ZODBMutablePropertyProvider as a example foreign property
provider.

"""
import io
from datetime import datetime

from Products.PlonePAS.Extensions.Install import activatePluginInterfaces
from Products.PlonePAS.plugins.property import ZODBMutablePropertyProvider

from plone import api
from ploneintranet import api as pi_api
from ploneintranet.userprofile.tests.base import BaseTestCase
from ploneintranet.userprofile.sync import IUserProfileManager
from ploneintranet.userprofile.sync import AllUsersPropertySync
from ploneintranet.userprofile.sync import NO_VALUE


TESTING_PLUGIN_ID = 'mock_ldap_properties'


def install_mock_properties_plugin():
    out = io.BytesIO()
    pp = ZODBMutablePropertyProvider(TESTING_PLUGIN_ID,
                                     'Mock LDAP Properties',
                                     schema=(('email', 'string', NO_VALUE), ))
    pp.meta_type = 'Mock PAS User Properties'
    acl_users = api.portal.get_tool('acl_users')
    acl_users[TESTING_PLUGIN_ID] = pp
    activatePluginInterfaces(api.portal.get(), TESTING_PLUGIN_ID, out)


class SyncBaseTestCase(BaseTestCase):

    def setUp(self):
        super(SyncBaseTestCase, self).setUp()
        install_mock_properties_plugin()

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
        plugin = acl_users[TESTING_PLUGIN_ID]
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
        upm = IUserProfileManager(user)
        upm.sync()
        self.assertEqual(user.email, email)
        catalog = api.portal.get_tool(name='portal_catalog')
        brains = catalog.searchResults(portal_type=user.portal_type)
        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0]['email'], email)
        self._check_set_last_sync(brains[0].getObject())

    def test_sync_local_user(self):
        self.login_as_portal_owner()
        user = self._create_userprofiles()
        ad = IUserProfileManager(user)
        ad.sync()
        self.assertFalse(
            hasattr(user, 'last_sync'),
            'User should not have been synced',
        )


class TestAllUsersPropertySync(SyncBaseTestCase):

    def test__call__(self):
        self.login_as_portal_owner()
        self._create_userprofiles()
        view = AllUsersPropertySync(self.profiles, self.request)
        view()
        self._check_set_last_sync(self.profiles)
