"""Tests for synchronisation of user profiles with external sources.

Re-uses the ZODBMutablePropertyProvider as a example foreign property
provider.

Re-uses the 'source_users' plugin in order to simulate a primary
external user source.

"""
import io
from datetime import datetime

from Products.PlonePAS.Extensions.Install import activatePluginInterfaces
from Products.PlonePAS.plugins.property import ZODBMutablePropertyProvider

from plone import api
from ploneintranet import api as pi_api
from ploneintranet.userprofile.sync import AllUsersPropertySync
from ploneintranet.userprofile.sync import AllUsersSync
from ploneintranet.userprofile.sync import IUserProfileManager
from ploneintranet.userprofile.sync import NO_VALUE
from ploneintranet.userprofile.sync import get_last_sync
from ploneintranet.userprofile.sync import record_last_sync
from ploneintranet.userprofile.tests.base import BaseTestCase

TESTING_PLUGIN_ID = 'mock_ldap'
TEST_USER_PREFIX = 'sync-user'


def install_mock_pas_plugin():
    out = io.BytesIO()
    pp = ZODBMutablePropertyProvider(TESTING_PLUGIN_ID,
                                     'Mock LDAP',
                                     schema=(('email', 'string', NO_VALUE), ))
    pp.meta_type = 'Mock External PAS Users'
    acl_users = api.portal.get_tool('acl_users')
    acl_users[TESTING_PLUGIN_ID] = pp
    activatePluginInterfaces(api.portal.get(), TESTING_PLUGIN_ID, out)


class SyncBaseTestCase(BaseTestCase):

    def setUp(self):
        super(SyncBaseTestCase, self).setUp()
        install_mock_pas_plugin()

    def _get_member_ids(self):
        user_ids = {user.getId() for user in api.user.get_users()}
        return {user_id
                for user_id in user_ids
                if user_id.startswith(TEST_USER_PREFIX)}

    def _get_userprofiles(self):
        return map(pi_api.userprofile.get, self._get_member_ids())

    def _create_userprofile(self):
        user = pi_api.userprofile.create(
            username='johndoe',
            email='johndoe@example.com',
            properties={
                'first_name': u'John',
                'last_name': u'Doe',
            },
            approve=True,
        )
        return user

    def _check_last_sync_set(self, context):
        self.assertIsInstance(context.last_sync, datetime)

    def _set_foreign_property(self, member, key, value):
        acl_users = api.portal.get_tool(name='acl_users')
        plugin = acl_users[TESTING_PLUGIN_ID]
        sheet = plugin.getPropertiesForUser(member)
        sheet.setProperty(member, key, value)


class TestUserPropertyManager(SyncBaseTestCase):

    def test_sync(self):
        self.login_as_portal_owner()
        user = self._create_userprofile()
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
        self._check_last_sync_set(brains[0].getObject())

    def test_sync_local_user(self):
        self.login_as_portal_owner()
        user = self._create_userprofile()
        ad = IUserProfileManager(user)
        ad.sync()
        self.assertFalse(
            hasattr(user, 'last_sync'),
            'User should not have been synced',
        )


class TestAllUsersPropertySync(SyncBaseTestCase):

    def test__call__(self):
        self.login_as_portal_owner()
        self._create_userprofile()
        view = AllUsersPropertySync(self.profiles, self.request)
        view()
        self._check_last_sync_set(self.profiles)


class TestAllUsersSync(SyncBaseTestCase):

    def _create_external_user(self, test_user_suffix):
        """Return a userid for tests."""
        username = '{}-{}'.format(TEST_USER_PREFIX, test_user_suffix)
        email = '{}@ploneintranet.org'.format(username)
        member = api.user.create(username=username, email=email)
        self._set_foreign_property(member, 'email', email)
        return username

    def _create_external_users(self, n):
        for i in range(n):
            self._create_external_user(i)

    def _check_profiles_synced(self, expected_userids, since=datetime.min):
        for userid in expected_userids:
            self.assertIn(userid, self.profiles)
            profile = self.profiles[userid]
            self._check_last_sync_set(profile)
            self.assertGreater(profile.last_sync, since)

    def _check_sync_dates(self):
        profiles = self._get_userprofiles()
        sync_start = self.profiles.last_sync
        not_disabled = lambda obj: api.content.get_state(obj=obj) != 'disabled'
        synced_profiles = filter(get_last_sync, profiles)
        synced_profiles = filter(not_disabled, synced_profiles)
        self.assertTrue(all(sync_start < profile.last_sync
                            for profile in synced_profiles))

    def _call_view_under_test(self):
        view = AllUsersSync(self.profiles, self.request)
        view()

    def setUp(self):
        super(SyncBaseTestCase, self).setUp()
        self.login_as_portal_owner()
        install_mock_pas_plugin()

    def test_no_profiles_synced(self):
        self._create_external_users(10)
        self._check_profiles_synced([])
        sync_dt = datetime.utcnow()
        self._call_view_under_test()
        member_ids = self._get_member_ids()
        self._check_profiles_synced(member_ids, sync_dt)
        self._check_sync_dates()

    def test_some_profiles_synced(self):
        self._create_external_users(9)

        # Simulate 1 profile already synced
        username = '{}-9'.format(TEST_USER_PREFIX)
        profile = pi_api.userprofile.create(username=username,
                                            approve=True)
        record_last_sync(profile)
        self._check_profiles_synced({profile.getId()})

        self._call_view_under_test()
        self._check_profiles_synced(self._get_member_ids())
        self._check_sync_dates()

    def test_all_profiles_synced(self):
        for n in range(3):
            username = '{}-{}'.format(TEST_USER_PREFIX, n)
            profile = pi_api.userprofile.create(username=username,
                                                approve=True)
            record_last_sync(profile)

        sync_dt = datetime.utcnow()
        self._call_view_under_test()
        self._check_profiles_synced([], sync_dt)

        # Simulate a new remote user being added
        sync_dt = datetime.utcnow()
        userid = self._create_external_user(3)
        self._call_view_under_test()
        self._check_profiles_synced({userid}, since=sync_dt)
        self._check_sync_dates()

    def test_external_user_removed_disables_profile(self):
        """Test the case where a remote user been deleted.

        The local membrane profile should be disabled.
        """
        username = self._create_external_user(0)
        self._call_view_under_test()
        api.user.delete(username=username)
        self._call_view_under_test()
        profile = pi_api.userprofile.get(username=username)
        self.assertIsNotNone(profile)
        self.assertEqual(api.content.get_state(obj=profile), 'disabled')
        self._check_sync_dates()

    def test_local_profile_is_not_disabled(self):
        """Test a "local" profile that has never been sync'd is not disabled.
        """
        username = TEST_USER_PREFIX + '-0'
        profile = pi_api.userprofile.create(username=username,
                                            approve=True)
        api.user.delete(username=username)
        self._call_view_under_test()
        profile = pi_api.userprofile.get(username=username)
        self.assertIsNotNone(profile)
        self.assertEqual(api.content.get_state(obj=profile), 'enabled')
        self.assertIsNone(get_last_sync(profile))
