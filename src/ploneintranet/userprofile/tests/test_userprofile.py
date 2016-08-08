# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from ZPublisher.HTTPRequest import FileUpload
from ZPublisher.HTTPRequest import ZopeFieldStorage
from ZPublisher.Iterators import IStreamIterator
from io import BytesIO
from plone import api
from plone.namedfile import NamedBlobImage
from ploneintranet.userprofile.browser.tiles.contacts_results import ContactsResults  # noqa
from ploneintranet.userprofile.browser.userprofile import AuthorView
from ploneintranet.userprofile.browser.userprofile import AvatarsView
from ploneintranet.userprofile.browser.userprofile import MyAvatar
from ploneintranet.userprofile.browser.userprofile import MyProfileView
from ploneintranet.userprofile.browser.userprofile import UserProfileView
from ploneintranet.userprofile.browser.userprofile import default_avatar
from ploneintranet.userprofile.tests.base import BaseTestCase
from zExceptions import NotFound
from zope.component import getMultiAdapter

import os

TEST_AVATAR_FILENAME = u'test_avatar.jpg'


class TestUserProfileBase(BaseTestCase):

    def setUp(self):
        super(TestUserProfileBase, self).setUp()
        self.login_as_portal_owner()
        username1 = 'johndoe'
        if username1 in self.profiles:
            self.profile1 = self.profiles[username1]
        else:
            self.profile1 = api.content.create(
                container=self.profiles,
                type='ploneintranet.userprofile.userprofile',
                id=username1,
                username=username1,
                first_name='John',
                last_name='Doe',
            )
            api.content.transition(self.profile1, 'approve')
            self.profile1.reindexObject()

        username2 = 'janedoe'
        if username2 in self.profiles:
            self.profile2 = self.profiles[username2]
        else:
            self.profile2 = api.content.create(
                container=self.profiles,
                type='ploneintranet.userprofile.userprofile',
                id=username2,
                username=username2,
                first_name='Jane',
                last_name='Doe',
            )
            api.content.transition(self.profile2, 'approve')
            self.profile2.reindexObject()

        self.logout()

    def create_test_file_field(self, data, filename):
        field_storage = ZopeFieldStorage()
        field_storage.file = BytesIO(data)
        field_storage.filename = filename
        file_field = FileUpload(field_storage)
        return file_field


class TestUserProfileView(TestUserProfileBase):

    def test_profile_container(self):
        ''' We want self.profiles, the profiles container to be public
        '''
        self.assertEqual(
            self.profiles.portal_type,
            'ploneintranet.userprofile.userprofilecontainer'
        )
        self.assertEqual(
            api.content.get_state(self.profiles),
            'published'
        )

    def test_is_me(self):
        profile_view = UserProfileView(self.profile1, self.request)

        self.login(self.profile1.username)
        self.assertTrue(profile_view.is_me())
        self.logout()

        self.login(self.profile2.username)
        self.assertFalse(profile_view.is_me())
        self.logout()

    def test__user_details(self):
        self.login(self.profile1.username)
        profile_view = UserProfileView(self.profile1, self.request)
        details = profile_view._user_details([
            self.profile1.username,
            self.profile2.username,
        ])
        self.assertEqual(len(details), 2)
        self.assertEqual(
            details[0]['title'], self.profile1.fullname,
        )
        self.assertEqual(
            details[1]['title'], self.profile2.fullname,
        )

    def test_recent_contacts_not_duplicated(self):
        self.login(self.profile1.username)
        profile_view = UserProfileView(self.profile2, self.request)
        profile_view._update_recent_contacts()
        self.assertIn(self.profile2.username,
                      self.profile1.recent_contacts or [])

        profile_view._update_recent_contacts()
        recent = self.profile1.recent_contacts or []
        self.assertEqual(
            recent.count(self.profile2.username), 1,
            "Recent contact entry duplicated")

    def test_recent_contacts_most_recent_first(self):
        self.profile1.recent_contacts = ['some_user']
        self.login(self.profile1.username)
        profile_view = UserProfileView(self.profile2, self.request)
        profile_view._update_recent_contacts()
        recent = self.profile1.recent_contacts or []
        self.assertEqual(recent[0], self.profile2.username)

    def test_recent_contacts_self_excluded(self):
        self.login(self.profile1.username)
        profile_view = UserProfileView(self.profile1, self.request)
        profile_view._update_recent_contacts()
        self.assertNotIn(
            self.profile1.username, self.profile1.recent_contacts or [])

    def test_recent_contacts_length_limited(self):
        self.profile1.recent_contacts = [
            'user{0}'.format(n) for n in range(20)]
        self.login(self.profile1.username)
        profile_view = UserProfileView(self.profile2, self.request)
        profile_view._update_recent_contacts()
        recent = self.profile1.recent_contacts or []
        self.assertLessEqual(len(recent), 20)


class TestContactsResults(TestUserProfileBase):

    def test_resolve_profile(self):
        self.profile1.recent_contacts = [self.profile2.username]
        self.login(self.profile1.username)
        contacts_results = ContactsResults(self.portal, self.request)
        recent = contacts_results.recent_contacts()
        self.assertEqual(recent[0], self.profile2)

    def test_invalid_users_dropped(self):
        self.profile1.recent_contacts = [
            'deleted_user', self.profile2.username]
        self.login(self.profile1.username)
        contacts_results = ContactsResults(self.portal, self.request)
        recent = contacts_results.recent_contacts()
        self.assertEqual(len(recent), 1)
        self.assertEqual(recent[0], self.profile2)

    def test_length_limited(self):
        # In practice a user will not be in recent_contacts multiple times. We
        # use this shortcut only to avoid creating 10 user profiles.
        self.profile1.recent_contacts = [self.profile2.username] * 11
        self.login(self.profile1.username)
        contacts_results = ContactsResults(self.portal, self.request)
        recent = contacts_results.recent_contacts()
        self.assertEqual(len(recent), 10)


class TestAuthorView(TestUserProfileBase):

    def test_call(self):
        self.login(self.profile2.username)
        author_view = AuthorView(self.portal, self.request)

        author_view.publishTraverse(self.request,
                                    self.profile1.username)
        redirect_url = author_view()
        self.assertEqual(
            redirect_url,
            self.profile1.absolute_url(),
        )

        author_view.publishTraverse(self.request,
                                    'not-a-username')
        with self.assertRaises(NotFound):
            author_view()


class TestMyProfileView(TestUserProfileBase):

    def test_call(self):
        self.login(self.profile2.username)
        myprofile_view = MyProfileView(self.portal, self.request)

        redirect_url = myprofile_view()
        self.assertEqual(
            redirect_url,
            self.profile2.absolute_url(),
        )

        self.logout()

        with self.assertRaises(Unauthorized):
            myprofile_view()


class TestAvatarViews(TestUserProfileBase):

    def setUp(self):
        super(TestAvatarViews, self).setUp()
        avatar_file = open(
            os.path.join(os.path.dirname(__file__),
                         TEST_AVATAR_FILENAME), 'r')
        self.profile1.portrait = NamedBlobImage(
            data=avatar_file.read(),
            filename=TEST_AVATAR_FILENAME)
        self.default_avatar = default_avatar(self.request.response)

    def test_avatars_view(self):
        self.login(self.profile1.username)
        avatars_view = AvatarsView(self.portal, self.request)
        avatars_view.publishTraverse(self.request,
                                     self.profile1.username)

        data = avatars_view()
        self.assertTrue(IStreamIterator.providedBy(data))

        avatars_view.publishTraverse(self.request,
                                     self.profile2.username)
        self.assertEqual(avatars_view(), self.default_avatar)

        avatars_view.publishTraverse(self.request,
                                     'not-a-username')
        self.assertEqual(avatars_view(), self.default_avatar)

    def test_my_avatar(self):
        self.login(self.profile1.username)
        my_avatar = MyAvatar(self.profile1, self.request)
        data = my_avatar()
        self.assertTrue(IStreamIterator.providedBy(data))

        profile_data = my_avatar.avatar_profile()
        self.assertTrue(IStreamIterator.providedBy(profile_data))

        avatar = MyAvatar(self.profile2, self.request)

        self.assertEqual(avatar(), self.default_avatar)

    def test_upload_avatar(self):
        self.login(self.profile1.username)
        self.request.form['submit'] = 'submit'
        avatar_file = open(
            os.path.join(os.path.dirname(__file__), TEST_AVATAR_FILENAME), 'r')
        self.request.form['portrait'] = self.create_test_file_field(
            avatar_file.read(), TEST_AVATAR_FILENAME)

        getMultiAdapter(
            (self.profile1, self.request), name='personal-menu.html')()
        self.assertEqual(self.profile1.portrait.filename, TEST_AVATAR_FILENAME)

    def test_upload_avatar_large(self):
        TEST_AVATAR_FILENAME_LARGE = u'test_avatar_large.jpg'
        self.login(self.profile2.username)
        self.request.form['submit'] = 'submit'
        avatar_file = open(
            os.path.join(
                os.path.dirname(__file__), TEST_AVATAR_FILENAME_LARGE),
            'r'
        )
        self.request.form['portrait'] = self.create_test_file_field(
            avatar_file.read(), TEST_AVATAR_FILENAME_LARGE)

        getMultiAdapter(
            (self.profile2, self.request), name='personal-menu.html')()
        self.assertEqual(
            self.profile2.portrait.filename, TEST_AVATAR_FILENAME_LARGE)
