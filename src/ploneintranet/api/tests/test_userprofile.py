from AccessControl import AuthEncoding
from zope.interface import Invalid
from zope.interface import directlyProvides
from plone import api as plone_api
from ploneintranet.api.testing import IntegrationTestCase
from ploneintranet import api as pi_api
from ploneintranet.userprofile.content.userprofile import UserProfile
from ploneintranet.userprofile.interfaces import IMembershipResolver


class TestUserProfile(IntegrationTestCase):

    def test_create(self):
        self.login_as_portal_owner()
        profile = pi_api.userprofile.create(
            username='johndoe',
            email='johndoe@doe.com',
            approve=True,
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

    def test_password_storage(self):
        password_plain = 'secret'
        profile = pi_api.userprofile.create(
            username='johndoe',
            email='johndoe@doe.com',
            password=password_plain,
            approve=True,
        )

        self.assertNotEqual(profile.password,
                            password_plain,
                            'Password not encrypted correctly')

        self.assertTrue(profile.password.startswith('{BCRYPT}'))
        self.assertTrue(
            AuthEncoding.pw_validate(
                profile.password,
                password_plain,
            )
        )

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

    def test_get_users_from_userids_and_groupids(self):
        """NB this overlaps with the getters tested below
        but operates on groups that are
        <class 'Products.PlonePAS.tools.groupdata.GroupData'>"""
        self.login_as_portal_owner()
        profile1 = pi_api.userprofile.create(
            username='janedoe',
            email='janedoe@doe.com',
        )
        profile2 = pi_api.userprofile.create(
            username='bobdoe',
            email='bobdoe@doe.com',
        )
        group1 = plone_api.group.create(groupname='group1')
        group1.addMember(profile2.getId())
        users = pi_api.userprofile.get_users_from_userids_and_groupids(
            ids=['janedoe', 'group1'])
        user_ids = [i.getId() for i in users]
        self.assertIn(profile1.getId(), user_ids)
        self.assertIn(profile2.getId(), user_ids)
        self.assertEqual(len(users), 2)


class TestUserProfileGetUsers(IntegrationTestCase):

    def setUp(self):
        IntegrationTestCase.setUp(self)
        self.login_as_portal_owner()
        self.profile1 = pi_api.userprofile.create(
            username='janedoe',
            email='janedoe@doe.com',
        )
        self.profile2 = pi_api.userprofile.create(
            username='bobdoe',
            email='bobdoe@doe.com',
        )
        self.folder = plone_api.content.create(
            self.portal, 'Folder', 'my-folder', 'My Folder')
        self.folder.members = ['bobdoe', ]
        directlyProvides(self.folder, IMembershipResolver)

    def test_get_users_rtype(self):
        """Verify default rtype for full_objects argument
        - this ought to change from objects to brains soon
        """
        usergen = pi_api.userprofile.get_users()
        retval = [x for x in usergen][0]
        self.assertFalse(hasattr(retval, 'getObject'))

    def test_get_users_brains(self):
        usergen = pi_api.userprofile.get_users(full_objects=False)
        self.assertEqual(sorted([x.email for x in usergen]),
                         ['bobdoe@doe.com', 'janedoe@doe.com'])

    def test_get_users_fullobj(self):
        usergen = pi_api.userprofile.get_users(full_objects=True)
        found = [x for x in usergen]
        self.assertEqual(len(found), 2)
        self.assertIn(self.profile1, found)
        self.assertIn(self.profile2, found)

    def test_get_users_context_workspace_fullobj(self):
        usergen = pi_api.userprofile.get_users(self.folder, True)
        found = [x for x in usergen]
        self.assertEqual(len(found), 1)
        self.assertNotIn(self.profile1, found)
        self.assertIn(self.profile2, found)

    def test_get_users_context_content_fullobj(self):
        page = plone_api.content.create(
            self.folder, 'Document', 'my-document', 'My Document')
        usergen = pi_api.userprofile.get_users(page, True)
        found = [x for x in usergen]
        self.assertEqual(len(found), 1)
        self.assertNotIn(self.profile1, found)
        self.assertIn(self.profile2, found)
