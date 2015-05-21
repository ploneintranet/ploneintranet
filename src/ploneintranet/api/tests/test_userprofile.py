from ploneintranet.api.testing import IntegrationTestCase
from ploneintranet import api as pi_api
from plone import api
from ploneintranet.userprofile.content.userprofile import UserProfile


class TestUserProfile(IntegrationTestCase):

    def test_create(self):
        profile = pi_api.userprofile.create(
            username='johndoe',
            email='johndoe@doe.com',
        )
        self.assertIsInstance(
            profile,
            UserProfile,
        )
        mtool = api.portal.get_tool('membrane_tool')
        mtool.reindexObject(profile)

        self.login('johndoe')

    def test_get(self):
        profile = pi_api.userprofile.create(
            username='janedoe',
            email='janedoe@doe.com',
        )
        profile2 = pi_api.userprofile.create(
            username='bobdoe',
            email='bobdoe@doe.com',
        )
        mtool = api.portal.get_tool('membrane_tool')
        mtool.reindexObject(profile)
        mtool.reindexObject(profile2)

        found = pi_api.userprofile.get('janedoe')
        self.assertEqual(found, profile)
        found = pi_api.userprofile.get('bobdoe')
        self.assertEqual(found, profile2)

        notfound = pi_api.userprofile.get('wigglesdoe')
        self.assertIsNone(notfound)

    def test_get_current(self):
        profile = pi_api.userprofile.create(
            username='janedoe',
            email='janedoe@doe.com',
        )
        profile2 = pi_api.userprofile.create(
            username='bobdoe',
            email='bobdoe@doe.com',
        )
        mtool = api.portal.get_tool('membrane_tool')
        api.content.transition(profile, 'approve')
        mtool.reindexObject(profile)
        api.content.transition(profile2, 'approve')
        mtool.reindexObject(profile2)

        self.login('janedoe')
        found = pi_api.userprofile.get_current()
        self.assertEqual(found, profile)

        self.login('bobdoe')
        found = pi_api.userprofile.get_current()
        self.assertEqual(found, profile2)
