from plone import api
from ploneintranet.userprofile.tests.base import BaseTestCase


class TestUserPropertySync(BaseTestCase):

    def _create_userprofiles(self):
        self.login_as_portal_owner()
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
        self.logout()

    def test_sync_properties(self):
        self._create_userprofiles()
