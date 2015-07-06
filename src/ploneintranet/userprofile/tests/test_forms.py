from zope import schema

from plone import api
from ploneintranet.userprofile.tests.base import BaseTestCase
from ploneintranet.userprofile.content.userprofile import IUserProfile
from ploneintranet.userprofile.content.userprofile import (
    IUserProfileAdditional
)
from ploneintranet.userprofile.browser.forms import icon_for_field
from ploneintranet.userprofile.browser.forms import get_fields_for_template
from ploneintranet.userprofile.browser.forms import UserProfileEditForm
from ploneintranet.userprofile.browser.forms import UserProfileViewForm


class TestUtilities(BaseTestCase):

    def test_icon_for_field(self):
        self.assertEqual(icon_for_field('email'),
                         'icon-mail')
        self.assertEqual(icon_for_field('this-is-not-a-known-field'),
                         'icon-right-open')


class TestUserProfileEditForm(BaseTestCase):

    def setUp(self):
        super(TestUserProfileEditForm, self).setUp()
        self.login_as_portal_owner()
        self.profile1 = api.content.create(
            container=self.profiles,
            type='ploneintranet.userprofile.userprofile',
            id='johndoe',
            username='johndoe',
            first_name='John',
            last_name='Doe',
        )

    def test_fields(self):
        form = UserProfileEditForm(self.profile1, self.request)
        form.update()
        fields = form.fields.keys()

        # By default should include all core fields apart from portrait
        for fieldname in schema.getFieldNames(IUserProfile):
            if fieldname != 'portrait':
                self.assertIn(
                    fieldname, fields,
                    '{0} missing from edit form'.format(fieldname)
                )

        # And any additional fields
        for fieldname in schema.getFieldNames(IUserProfileAdditional):
            self.assertIn(
                'IUserProfileAdditional.{0}'.format(fieldname),
                fields,
                '{0} missing from edit form'.format(fieldname)
            )

    def test_hidden_fields(self):
        api.portal.set_registry_record(
            'ploneintranet.userprofile.hidden_fields',
            (u'first_name', u'last_name', ),
        )

        form = UserProfileEditForm(self.profile1, self.request)
        form.update()
        fields = form.fields.keys()

        self.assertNotIn('first_name', fields)
        self.assertNotIn('last_name', fields)

    def test_read_only_fields(self):
        api.portal.set_registry_record(
            'ploneintranet.userprofile.read_only_fields',
            (u'first_name', u'last_name', ),
        )

        form = UserProfileEditForm(self.profile1, self.request)
        form.update()
        fields = form.fields.keys()

        self.assertIn('first_name', fields)
        self.assertIn('last_name', fields)

        self.assertEqual(form.widgets['first_name'].mode,
                         'display')
        self.assertEqual(form.widgets['last_name'].mode,
                         'display')


class TestUserProfileViewForm(BaseTestCase):

    def setUp(self):
        super(TestUserProfileViewForm, self).setUp()
        self.login_as_portal_owner()
        self.profile1 = api.content.create(
            container=self.profiles,
            type='ploneintranet.userprofile.userprofile',
            id='johndoe',
            username='johndoe',
            first_name='John',
            last_name='Doe',
            email='john@doe.com',
        )

    def test_hidden_fields(self):
        api.portal.set_registry_record(
            'ploneintranet.userprofile.hidden_fields',
            (u'first_name', u'last_name', ),
        )

        form = UserProfileViewForm(self.profile1, self.request)
        form.update()
        fields = form.fields.keys()

        self.assertNotIn('first_name', fields)
        self.assertNotIn('last_name', fields)

    def test_get_fields(self):
        form = UserProfileViewForm(self.profile1, self.request)
        form.update()
        fields = form.fields.keys()

        fields_for_template = get_fields_for_template(form)
        names = [x['name'] for x in fields_for_template]

        self.assertEqual(names, fields)

        mapping = dict([(x['name'], x) for x in fields_for_template])
        email = mapping['email']
        self.assertEqual(email['raw'], 'john@doe.com')
        self.assertEqual(email['label'], 'Email')
