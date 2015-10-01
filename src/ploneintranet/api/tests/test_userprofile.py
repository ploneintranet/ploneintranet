from zope.interface import Invalid
from plone import api as plone_api
from ploneintranet.api.testing import IntegrationTestCase
from ploneintranet import api as pi_api
from ploneintranet.userprofile.content.userprofile import UserProfile


class TestUserProfile(IntegrationTestCase):

    def test_create(self):
        self.login_as_portal_owner()
        profile = pi_api.userprofile.create(
            username='johndoe',
            email='johndoe@doe.com',
        )
        self.assertIsInstance(
            profile,
            UserProfile,
        )

        # Should have been added to global members group
        # and have Member role
        self.assertIn(
            'johndoe',
            plone_api.group.get(groupname='Members').getMemberIds()
        )
        self.assertIn(
            'Member',
            plone_api.user.get_roles(username='johndoe'),
        )

        # We can now login
        self.login('johndoe')

        # Cannot create another with same username
        self.login_as_portal_owner()
        with self.assertRaises(Invalid):
            pi_api.userprofile.create(
                username='johndoe',
                email='foobar@doe.com',
            )

    def test_get_users(self):
        self.login_as_portal_owner()
        profile1 = pi_api.userprofile.create(
            username='janedoe',
            email='janedoe@doe.com',
        )
        profile2 = pi_api.userprofile.create(
            username='bobdoe',
            email='bobdoe@doe.com',
        )
        found = [x for x in pi_api.userprofile.get_users()]
        self.assertEqual(len(found), 2)
        self.assertIn(profile1, found)
        self.assertIn(profile2, found)

    def test_get(self):
        self.login_as_portal_owner()
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
        self.login_as_portal_owner()
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

    def test_avatar_url(self):
        self.login_as_portal_owner()
        profile = pi_api.userprofile.create(
            username='janedoe',
            email='janedoe@doe.com',
            approve=True,
        )

        valid_url = pi_api.userprofile.avatar_url(profile.username)
        self.assertEqual(
            valid_url,
            '{portal_url}/@@avatars/{userid}'.format(
                portal_url=self.portal.absolute_url(),
                userid=profile.username,
            )
        )
