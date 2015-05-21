from zope.interface import Invalid

from ploneintranet.api.testing import IntegrationTestCase
from ploneintranet import api as pi_api
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

        self.login('johndoe')

        # Cannot create another with same username
        with self.assertRaises(Invalid):
            pi_api.userprofile.create(
                username='johndoe',
                email='foobar@doe.com',
            )

    def test_get(self):
        profile = pi_api.userprofile.create(
            username='janedoe',
            email='janedoe@doe.com',
        )
        profile2 = pi_api.userprofile.create(
            username='bobdoe',
            email='bobdoe@doe.com',
        )

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
            approve=True,
        )
        profile2 = pi_api.userprofile.create(
            username='bobdoe',
            email='bobdoe@doe.com',
            approve=True,
        )

        self.login('janedoe')
        found = pi_api.userprofile.get_current()
        self.assertEqual(found, profile)

        self.login('bobdoe')
        found = pi_api.userprofile.get_current()
        self.assertEqual(found, profile2)
