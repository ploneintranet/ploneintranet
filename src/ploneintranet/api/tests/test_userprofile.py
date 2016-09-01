import collections
import re
from AccessControl import AuthEncoding
from zope.interface import Invalid
from zope.interface import directlyProvides
from plone import api as plone_api
from plone.namedfile import NamedBlobImage
from ploneintranet.api.testing import IntegrationTestCase
from ploneintranet import api as pi_api
from ploneintranet.userprofile.content.userprofile import UserProfile
from ploneintranet.userprofile.interfaces import IMemberGroup
from ploneintranet.network.interfaces import INetworkTool
from zope.component import queryUtility


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

    def test_avatar_tag_no_portrait(self):
        self.login_as_portal_owner()
        profile = pi_api.userprofile.create(
            username='janedoe',
            email='janedoe@doe.com',
            approve=True,
            properties={
                'fullname': 'Jane Doe',
            },
        )

        self.maxDiff = None
        tag_no_link = re.sub('[ \n]+', ' ', pi_api.userprofile.avatar_tag(
            username='janedoe', link_to=None))
        self.assertEqual(
            tag_no_link,
            u' <span class="pat-avatar avatar" data-initials="{initials}" '
            'title="" > '
            '<img src="{portal_url}/profiles/{userid}/@@avatar_profile.jpg" '
            'alt="Image of {fullname}" class="default-user" '
            'i18n:attributes="alt"> '
            '</span>'
            ''.format(
                portal_url=self.portal.absolute_url(),
                userid=profile.username,
                fullname=profile.fullname,
                initials=profile.initials,
            ))

        tag_link_profile = re.sub('[ \n]+', ' ', pi_api.userprofile.avatar_tag(
            username='janedoe', link_to='profile'))
        self.assertEqual(
            tag_link_profile,
            u' <a href="{portal_url}/profiles/{userid}" '
            'class="pat-avatar avatar" data-initials="{initials}" title="" > '
            '<img src="{portal_url}/profiles/{userid}/@@avatar_profile.jpg" '
            'alt="Image of {fullname}" class="default-user" '
            'i18n:attributes="alt"> '
            '</a>'
            ''.format(
                portal_url=self.portal.absolute_url(),
                userid=profile.username,
                fullname=profile.fullname,
                initials=profile.initials,
            ))

        tag_link_image = re.sub('[ \n]+', ' ', pi_api.userprofile.avatar_tag(
            username='janedoe', link_to='image'))
        self.assertEqual(
            tag_link_image,
            u' <a class="pat-avatar avatar user-info-avatar" '
            'data-initials="{initials}" title="" > '
            '<img src="{portal_url}/profiles/{userid}/@@avatar_profile.jpg" '
            'alt="Image of {fullname}" class="default-user" '
            'i18n:attributes="alt"> '
            '</a>'

            ''.format(
                portal_url=self.portal.absolute_url(),
                userid=profile.username,
                fullname=profile.fullname,
                initials=profile.initials,
            ))

    def test_avatar_tag_with_portrait(self):
        self.login_as_portal_owner()
        profile = pi_api.userprofile.create(
            username='janedoe',
            email='janedoe@doe.com',
            approve=True,
            properties={
                'fullname': 'Jane Doe',
            },
        )
        profile.portrait = NamedBlobImage(
            data='GIF89a;',
            filename=u'avatar.png')

        self.maxDiff = None
        tag_no_link = re.sub('[ \n]+', ' ', pi_api.userprofile.avatar_tag(
            username='janedoe', link_to=None))
        self.assertEqual(
            tag_no_link,
            u' <span class="pat-avatar avatar" data-initials="{initials}" '
            'title="" > '
            '<img src="{portal_url}/profiles/{userid}/@@avatar_profile.jpg" '
            'alt="Image of {fullname}" class="" '
            'i18n:attributes="alt"> '
            '</span>'
            ''.format(
                portal_url=self.portal.absolute_url(),
                userid=profile.username,
                fullname=profile.fullname,
                initials=profile.initials,
            ))

        tag_link_profile = re.sub('[ \n]+', ' ', pi_api.userprofile.avatar_tag(
            username='janedoe', link_to='profile'))
        self.assertEqual(
            tag_link_profile,
            u' <a href="{portal_url}/profiles/{userid}" '
            'class="pat-avatar avatar" data-initials="{initials}" title="" > '
            '<img src="{portal_url}/profiles/{userid}/@@avatar_profile.jpg" '
            'alt="Image of {fullname}" class="" '
            'i18n:attributes="alt"> '
            '</a>'
            ''.format(
                portal_url=self.portal.absolute_url(),
                userid=profile.username,
                fullname=profile.fullname,
                initials=profile.initials,
            ))

        tag_link_image = re.sub('[ \n]+', ' ', pi_api.userprofile.avatar_tag(
            username='janedoe', link_to='image'))
        self.assertEqual(
            tag_link_image,
            u' <a href="{portal_url}/profiles/{userid}/@@avatar_profile.jpg" '
            'class="pat-avatar avatar pat-gallery user-info-avatar" '
            'data-initials="{initials}" title="" > '
            '<img src="{portal_url}/profiles/{userid}/@@avatar_profile.jpg" '
            'alt="Image of {fullname}" class="" '
            'i18n:attributes="alt"> '
            '</a>'

            ''.format(
                portal_url=self.portal.absolute_url(),
                userid=profile.username,
                fullname=profile.fullname,
                initials=profile.initials,
            ))

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
        self.profile3 = pi_api.userprofile.create(
            username='bobschmo',
            email='bobschmo@schmo.com'
        )
        self.profile4 = pi_api.userprofile.create(
            username='celinedijon',
            email='celine@dijon.com'
        )
        self.group1 = plone_api.group.create(groupname='group1')
        self.group1.addMember(self.profile4.getId())
        self.folder = plone_api.content.create(
            self.portal, 'Folder', 'my-folder', 'My Folder')
        self.folder.members = ['bobdoe', 'bobschmo']
        directlyProvides(self.folder, IMemberGroup)

    def test_get_users_rtype_user(self):
        """Verify default rtype for full_objects argument
        - this ought to change from objects to brains soon
        """
        usergen = pi_api.userprofile.get_users()
        retval = [x for x in usergen][0]
        self.assertFalse(hasattr(retval, 'getObject'))

    def test_get_users_rtype_iterator_nofullobjects(self):
        """Verify that rtype is iterator
        """
        usergen = pi_api.userprofile.get_users()
        self.assertTrue(isinstance(usergen, collections.Iterator))

    def test_get_users_rtype_iterator_fullobjects(self):
        """Verify that rtype is iterator
        """
        usergen = pi_api.userprofile.get_users()
        self.assertTrue(isinstance(usergen, collections.Iterator))

    def test_get_users_brains_userid(self):
        usergen = pi_api.userprofile.get_users(full_objects=False)
        self.assertEqual(
            sorted([x.getUserId for x in usergen]),
            ['bobdoe', 'bobschmo', 'celinedijon', 'janedoe'])

    def test_get_users_brains_email(self):
        usergen = pi_api.userprofile.get_users(full_objects=False)
        self.assertEqual(
            sorted([x.email for x in usergen]),
            ['bobdoe@doe.com', 'bobschmo@schmo.com',
             'celine@dijon.com', 'janedoe@doe.com'])

    def test_get_users_fullobj(self):
        usergen = pi_api.userprofile.get_users(full_objects=True)
        found = [x for x in usergen]
        self.assertEqual(len(found), 4)
        self.assertIn(self.profile1, found)
        self.assertIn(self.profile2, found)
        self.assertIn(self.profile3, found)
        self.assertIn(self.profile4, found)

    def test_get_users_context_workspace_fullobj(self):
        usergen = pi_api.userprofile.get_users(self.folder, True)
        found = [x for x in usergen]
        self.assertEqual(len(found), 2)
        self.assertNotIn(self.profile1, found)
        self.assertIn(self.profile2, found)
        self.assertIn(self.profile3, found)

    def test_get_users_context_content_fullobj(self):
        page = plone_api.content.create(
            self.folder, 'Document', 'my-document', 'My Document')
        usergen = pi_api.userprofile.get_users(page, True)
        found = [x for x in usergen]
        self.assertEqual(len(found), 2)
        self.assertNotIn(self.profile1, found)
        self.assertIn(self.profile2, found)
        self.assertIn(self.profile3, found)

    def test_get_users_context_workspace_group_lookup(self):
        folder = plone_api.content.create(
            self.portal, 'Folder', 'my-folder-with-group', 'My Folder')
        folder.members = ['bobdoe', 'bobschmo', 'group1']
        directlyProvides(folder, IMemberGroup)
        usergen = pi_api.userprofile.get_users(folder, True)
        found = [x for x in usergen]
        self.assertEqual(len(found), 3)
        self.assertNotIn(self.profile1, found)
        self.assertIn(self.profile2, found)
        self.assertIn(self.profile3, found)
        self.assertIn(self.profile4, found)

    def test_get_users_search_fulltext_1(self):
        usergen = pi_api.userprofile.get_users(
            full_objects=False, SearchableText=u'bob*')
        self.assertEqual(
            sorted([x.getUserId for x in usergen]), ['bobdoe', 'bobschmo'])

    def test_get_users_search_fulltext_2(self):
        usergen = pi_api.userprofile.get_users(
            full_objects=False, SearchableText=u'doe.com')
        self.assertEqual(
            sorted([x.getUserId for x in usergen]), ['bobdoe', 'janedoe'])

    def test_get_users_context_search_fulltext(self):
        usergen = pi_api.userprofile.get_users(
            context=self.folder, full_objects=False, SearchableText=u'doe.com')
        self.assertEqual(
            sorted([x.getUserId for x in usergen]), ['bobdoe', ])

    def test_get_users_exactgetusername(self):
        usergen = pi_api.userprofile.get_users(
            full_objects=True,
            exact_getUserName=['janedoe', 'bobdoe'])
        found = [x for x in usergen]
        self.assertEqual(len(found), 2)
        self.assertIn(self.profile1, found)
        self.assertIn(self.profile2, found)

    def test_get_users_context_exactgetusername_1(self):
        """Specifiying both a context and exact_getUserName
        returns the intersection of both results
        """
        usergen = pi_api.userprofile.get_users(
            context=self.folder,
            full_objects=True,
            exact_getUserName=['janedoe', 'bobdoe'])
        found = [x for x in usergen]
        self.assertEqual(len(found), 1)
        self.assertNotIn(self.profile1, found)
        self.assertIn(self.profile2, found)

    def test_get_users_context_exactgetusername_2(self):
        """Specifiying both a context and exact_getUserName
        returns the intersection of both results
        """
        usergen = pi_api.userprofile.get_users(
            context=self.folder,
            full_objects=True,
            exact_getUserName=['janedoe'])
        found = [x for x in usergen]
        self.assertEqual(len(found), 0)
        self.assertNotIn(self.profile1, found)
        self.assertNotIn(self.profile2, found)


class TestUserProfileGetUserSuggestions(IntegrationTestCase):

    def setUp(self):
        IntegrationTestCase.setUp(self)
        self.login_as_portal_owner()
        self.profiles_1 = [pi_api.userprofile.create(
            username=u'bobschmo-%s' % x,
            email=u'bobschmo-%s@schmo.com' % x,
        ) for x in range(8)]
        self.profiles_2 = [pi_api.userprofile.create(
            username=u'bobdoe-%s' % x,
            email=u'bobdoe-%s@doe.com' % x,
        ) for x in range(8)]
        self.profiles_3 = [pi_api.userprofile.create(
            username=u'maryjane-%s' % x,
            email=u'maryjane-%s@doe.com' % x,
        ) for x in range(8)]
        self.folder = plone_api.content.create(
            self.portal, 'Folder', 'my-folder', 'My Folder')

    def test_suggestions_all(self):
        """Default unfiltered"""
        usergen = pi_api.userprofile.get_user_suggestions(full_objects=True)
        found = set([x for x in usergen])
        self.assertEquals(found, set(self.profiles_1 +
                                     self.profiles_2 +
                                     self.profiles_3))

    def test_suggestions_context_overlimit(self):
        """Context provides enough"""
        self.folder.members = [u'maryjane-%x' % x for x in range(8)]
        directlyProvides(self.folder, IMemberGroup)
        usergen = pi_api.userprofile.get_user_suggestions(
            self.folder, full_objects=True)
        found = set([x for x in usergen])
        self.assertEquals(found, set(self.profiles_3))

    def test_suggestions_context_underlimit(self):
        """Context too small, fallback to all users"""
        self.folder.members = [u'maryjane-%x' % x for x in range(8)]
        directlyProvides(self.folder, IMemberGroup)
        usergen = pi_api.userprofile.get_user_suggestions(
            self.folder, full_objects=True, min_matches=10)
        found = set([x for x in usergen])
        self.assertEquals(found, set(self.profiles_1 +
                                     self.profiles_2 +
                                     self.profiles_3))

    def test_suggestions_context_search_overlimit(self):
        """Context provides enough"""
        self.folder.members = [u'bobschmo-%x' % x for x in range(8)]
        directlyProvides(self.folder, IMemberGroup)
        q = {'SearchableText': 'bob*'}
        usergen = pi_api.userprofile.get_user_suggestions(
            self.folder, full_objects=True, **q)
        found = set([x for x in usergen])
        self.assertEquals(found, set(self.profiles_1))

    def test_suggestions_context_search_underlimit(self):
        """Context provides enough"""
        self.folder.members = [u'bobschmo-%x' % x for x in range(8)]
        directlyProvides(self.folder, IMemberGroup)
        q = {'SearchableText': 'bob*'}
        usergen = pi_api.userprofile.get_user_suggestions(
            self.folder, full_objects=True, min_matches=10, **q)
        found = set([x for x in usergen])
        self.assertEquals(found, set(self.profiles_1 +
                                     self.profiles_2))

    def test_suggestions_network_overlimit(self):
        """Network provides enough"""
        graph = queryUtility(INetworkTool)
        # current user is 'admin'
        for x in range(8):
            graph.follow('user', u'bobdoe-%s' % x, 'admin')
        usergen = pi_api.userprofile.get_user_suggestions(
            None, full_objects=True)
        found = set([x for x in usergen])
        self.assertEquals(found, set(self.profiles_2))

    def test_suggestions_network_underlimit(self):
        """Network too small, fall back to all users"""
        graph = queryUtility(INetworkTool)
        # current user is 'admin'
        for x in range(8):
            graph.follow('user', u'bobdoe-%s' % x, 'admin')
        usergen = pi_api.userprofile.get_user_suggestions(
            None, full_objects=True, min_matches=10)
        found = set([x for x in usergen])
        self.assertEquals(found, set(self.profiles_1 +
                                     self.profiles_2 +
                                     self.profiles_3))

    def test_suggestions_context_network_overlimit(self):
        """Context and network combined provide enough"""
        self.folder.members = [u'maryjane-%x' % x for x in range(8)]
        directlyProvides(self.folder, IMemberGroup)
        graph = queryUtility(INetworkTool)
        # current user is 'admin'
        for x in range(8):
            graph.follow('user', u'bobdoe-%s' % x, 'admin')
        usergen = pi_api.userprofile.get_user_suggestions(
            self.folder, full_objects=True, min_matches=10)
        found = set([x for x in usergen])
        self.assertEquals(found, set(self.profiles_2 +
                                     self.profiles_3))

    def test_suggestions_context_network_overlap(self):
        """Context and network combined provide enough.
        Users matching both sets are listed only once.
        """
        self.folder.members = [u'maryjane-%x' % x for x in range(8)]
        directlyProvides(self.folder, IMemberGroup)
        graph = queryUtility(INetworkTool)
        # current user is 'admin'
        for x in range(8):
            graph.follow('user', u'bobdoe-%s' % x, 'admin')
        for x in range(4):
            graph.follow('user', u'maryjane-%s' % x, 'admin')
        usergen = pi_api.userprofile.get_user_suggestions(
            self.folder, full_objects=True, min_matches=10)
        found = set([x for x in usergen])
        self.assertEquals(len(found), 16)
        self.assertEquals(found, set(self.profiles_2 +
                                     self.profiles_3))

    def test_suggestions_context_network_underlimit(self):
        """The combination of context and network is not enough"""
        self.folder.members = [u'maryjane-%x' % x for x in range(8)]
        directlyProvides(self.folder, IMemberGroup)
        graph = queryUtility(INetworkTool)
        # current user is 'admin'
        for x in range(8):
            graph.follow('user', u'bobdoe-%s' % x, 'admin')
        usergen = pi_api.userprofile.get_user_suggestions(
            self.folder, full_objects=True, min_matches=20)
        found = set([x for x in usergen])
        self.assertEquals(found, set(self.profiles_1 +
                                     self.profiles_2 +
                                     self.profiles_3))

    def test_suggestions_context_network_underlimit_waybeyond(self):
        """The treshold is bigger than all users, check optimization."""
        self.folder.members = [u'maryjane-%x' % x for x in range(8)]
        directlyProvides(self.folder, IMemberGroup)
        graph = queryUtility(INetworkTool)
        # current user is 'admin'
        for x in range(8):
            graph.follow('user', u'bobdoe-%s' % x, 'admin')
        usergen = pi_api.userprofile.get_user_suggestions(
            self.folder, full_objects=True, min_matches=30)
        found = set([x for x in usergen])
        self.assertEquals(found, set(self.profiles_1 +
                                     self.profiles_2 +
                                     self.profiles_3))
