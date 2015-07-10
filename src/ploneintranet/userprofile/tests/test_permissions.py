# -*- coding: utf-8 -*-
from plone import api
from ploneintranet.userprofile.tests.base import BaseTestCase


class TestUserProfileLocalRoleAdapter(BaseTestCase):

    def setUp(self):
        super(TestUserProfileLocalRoleAdapter, self).setUp()
        self.login_as_portal_owner()
        self.profile1 = api.content.create(
            container=self.profiles,
            type='ploneintranet.userprofile.userprofile',
            id='johndoe',
            username='johndoe',
            first_name='John',
            last_name='Doe',
        )
        api.content.transition(self.profile1, 'approve')
        self.profile1.reindexObject()

        self.profile2 = api.content.create(
            container=self.profiles,
            type='ploneintranet.userprofile.userprofile',
            id='janedoe',
            username='janedoe',
            first_name='Jane',
            last_name='Doe',
        )
        api.content.transition(self.profile2, 'approve')
        self.profile2.reindexObject()

        self.logout()

    def test_owner_role(self):
        # We should get owner on our own profile
        # along with modify
        self.login(self.profile1.username)
        self.assertIn(
            'Owner',
            api.user.get_roles(obj=self.profile1)
        )
        self.assertTrue(
            api.user.get_permissions(obj=self.profile1)[
                'Modify portal content'
            ]
        )
        # Not on another user's profile
        self.assertNotIn(
            'Owner',
            api.user.get_roles(obj=self.profile2)
        )
        self.assertFalse(
            api.user.get_permissions(obj=self.profile2)[
                'Modify portal content'
            ]
        )
