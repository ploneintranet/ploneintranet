# -*- coding: utf-8 -*-
from zope.component import getMultiAdapter
from zope.interface import Invalid
from z3c.form.interfaces import IValidator

from plone import api as plone_api

from ploneintranet.userprofile.content.userprofile import IUserProfile
from ploneintranet.userprofile.tests.base import BaseTestCase


class TestValidators(BaseTestCase):

    """Test validators."""

    def test_username_is_unique(self):
        """Test that username is unique amongst users."""
        params = {
            'username': u'johndoe',
            'first_name': u'John',
            'last_name': u'Doe',
            'email': u"johndoe@example.com",
            'password': u'secret',
            'confirm_password': u'secret'}
        profile = plone_api.content.create(
            container=self.profiles,
            type='ploneintranet.userprofile.userprofile',
            id='johndoe',
            **params)
        plone_api.content.transition(profile, 'approve')

        # janedoe is not used
        validator = getMultiAdapter(
            (profile, self.request, None, IUserProfile['username'], None),
            IValidator)
        self.assertIsNone(validator.validate(u'janedoe'))

        # if context is the user that has this value as username, do not raise
        self.assertIsNone(validator.validate(u'johndoe'))

        # if context is another user, raise Invalid
        validator.context = self.profiles
        with self.assertRaises(Invalid):
            validator.validate(u'johndoe')
