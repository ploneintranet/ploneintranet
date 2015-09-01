"""
The following tests use ZODBMutablePropertyProvider ('mutable_properties)
as a example foreign property provider.
"""

from plone import api
from ploneintranet import api as pi_api
from ploneintranet.userprofile.tests.base import BaseTestCase
from ploneintranet.userprofile.browser.sync import IUserProfileManager


def _create_userprofiles(container):
    user = api.content.create(
        container=container,
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


def set_foreign_property(member, key, value):
    acl_users = api.portal.get_tool(name='acl_users')
    plugin = acl_users['mutable_properties']
    sheet = plugin.getPropertiesForUser(member)
    sheet.setProperty(member, key, value)


class TestUserPropertyManager(BaseTestCase):

    def test_sync(self):
        self.login_as_portal_owner()
        user = _create_userprofiles(self.profiles)
        member = api.user.get(username=user.username)
        email = 'test@foo.com'
        set_foreign_property(member, 'email', email)

        user = pi_api.userprofile.get(user.username)
        IUserProfileManager(user).sync()
        self.assertEqual(user.email, email)
        catalog = api.portal.get_tool(name='portal_catalog')
        brains = catalog.searchResults(portal_type=user.portal_type)
        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0]['email'], email)
