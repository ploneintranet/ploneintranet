# -*- coding: utf-8 -*-
from plone import api

from ploneintranet.userprofile.tests.base import BaseTestCase


class TestAuth(BaseTestCase):

    def setUp(self):
        super(TestAuth, self).setUp()
        self.login_as_portal_owner()
        params = {
            'username': 'franknfurter',
            'first_name': u'Frank N',
            'last_name': u'Furter',
            'email': "frankn@furter.com",
            'password': 'secret',
            'confirm_password': 'secret'}
        api.content.create(
            container=self.profiles,
            type='ploneintranet.userprofile.userprofile',
            id='franknfurter',
            **params)

    def test_profile_is_membrane_type(self):
        self.assertIn(
            'ploneintranet.userprofile.userprofile',
            self.membrane_tool.listMembraneTypes())

    def test_user_login(self):
        params = {
            'username': 'johndoe',
            'first_name': u'John',
            'last_name': u'Doe',
            'email': "johndoe@example.com",
            'password': 'secret',
            'confirm_password': 'secret'}
        profile = api.content.create(
            container=self.profiles,
            type='ploneintranet.userprofile.userprofile',
            id='johndoe',
            **params)

        self.logout()
        self.login('johndoe')
        user = api.user.get_current()
        self.assertEqual(
            profile.username,
            user.getUserName())

        self.logout()
        with self.assertRaises(ValueError):
            self.login('janedoe')

    def test_mail_password_form(self):
        self.login("franknfurter")
        view = self.portal.restrictedTraverse(
            '{0}/change-password'.format(
                '/'.join(self.portal.getPhysicalPath())))
        contents = view()
        self.assertIn("Change password", contents)

    def test_mail_password_form_disabled(self):
        """
        If the respective registry entry is set to False, the form for changing
        the password is not enabled.
        """
        self.login_as_portal_owner()
        api.portal.set_registry_record(
            "ploneintranet.userprofile.enable_password_reset", False)
        self.logout()
        self.login("franknfurter")
        view = self.portal.restrictedTraverse(
            '{0}/change-password'.format(
                '/'.join(self.portal.getPhysicalPath())))
        self.assertEquals(view(), '')
