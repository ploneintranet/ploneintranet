from plone import api
from ploneintranet.userprofile.tests.base import BaseTestCase
from ploneintranet.userprofile.browser.sync import UserPropertySync


class TestUserPropertySync(BaseTestCase):
    """The following tests use ZODBMutablePropertyProvider ('mutable_properties)
    as a example foreign property provider.
    """

    def _create_userprofiles(self):
        api.content.create(
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

    def test_sync_properties(self):
        self.login_as_portal_owner()
        self._create_userprofiles()
        sync_view = UserPropertySync(self.portal, self.request)
        self.assertEqual(
            sync_view.sync_properties(), 1)
