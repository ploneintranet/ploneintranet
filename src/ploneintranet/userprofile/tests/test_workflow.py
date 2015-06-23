# -*- coding: utf-8 -*-
from plone import api
from plone.api.exc import InvalidParameterError
from zExceptions import Unauthorized

from ploneintranet.userprofile.tests.base import BaseTestCase


class TestUserProfilePermissions(BaseTestCase):

    def setUp(self):
        super(TestUserProfilePermissions, self).setUp()
        self.login_as_portal_owner()
        api.user.create(email='bob@hotmail.com',
                        username='bob')
        self.logout()

    def test_add_container_permissions(self):
        self.login('bob')
        with self.assertRaises(Unauthorized):
            api.content.create(
                title="Profiles",
                type="ploneintranet.userprofile.userprofilecontainer",
                container=self.portal)

        api.user.grant_roles(username='bob',
                             roles=['Manager', ])
        self.login('bob')
        api.content.create(
            title="Profiles",
            type="ploneintranet.userprofile.userprofilecontainer",
            container=self.portal)

    def test_add_user_permissions(self):
        self.login('bob')
        with self.assertRaises(Unauthorized):
            api.content.create(
                id='another-user',
                username="another-user",
                type="ploneintranet.userprofile.userprofile",
                container=self.profiles)

        api.user.grant_roles(username='bob',
                             roles=['Site Administrator', ])
        self.login('bob')
        api.content.create(
            id='another-user',
            username="another-user",
            type="ploneintranet.userprofile.userprofile",
            container=self.profiles)

    def test_approve_user_permissions(self):
        self.login_as_portal_owner()
        profile = api.content.create(
            id='another-user',
            username="another-user",
            type="ploneintranet.userprofile.userprofile",
            container=self.profiles)

        self.login('bob')
        api.user.grant_roles(username='bob',
                             roles=['Reviewer', ])
        with self.assertRaises(InvalidParameterError):
            api.content.transition(profile, 'approve')

        api.user.grant_roles(username='bob',
                             roles=['Site Administrator', ])
        self.login('bob')
        api.content.transition(profile, 'approve')
