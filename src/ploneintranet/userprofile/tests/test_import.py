import os
import tablib

from Products.membrane.interfaces import IMembraneUserAuth
from Products.statusmessages.interfaces import IStatusMessage
from plone import api
from plone.app.contenttypes.tests.test_image import dummy_image
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.schema import invalidate_cache
from plone.directives import form
from ploneintranet import api as pi_api
from ploneintranet.userprofile import exc as custom_exc
from ploneintranet.userprofile.browser.user_import import CSVImportView
from ploneintranet.userprofile.browser.user_import import ImportAvatarsView
from ploneintranet.userprofile.browser.user_import import USER_PORTAL_TYPE
from ploneintranet.userprofile.tests.base import BaseTestCase
from zope import schema
from zope.component import getUtility
from zope.interface import alsoProvides


class IDummySchema(form.Schema):

    hair_colour = schema.TextLine(
        title=u'Hair colour')
alsoProvides(IDummySchema, IFormFieldProvider)


class TestAvatarImportView(BaseTestCase):

    def setUp(self):
        super(TestAvatarImportView, self).setUp()
        self.login_as_portal_owner()
        self.avatars = api.content.create(
            self.portal, 'Folder', title='Avatars')
        api.content.create(
            self.avatars, 'Image', title='scott.tiger.jpg',
            image=dummy_image())

        api.content.create(
            self.avatars, 'Image', title='john-doe.jpg',
            image=dummy_image())

        self.scott = pi_api.userprofile.create(
            'scott.tiger', 'scott@oracle.com')
        self.john = pi_api.userprofile.create(
            'john_doe', 'johndoe@example.com')

    def test_import(self):
        # plone normalized the image filename
        self.assertTrue('scott-tiger.jpg' in self.avatars.objectIds())
        self.assertFalse('scott.tiger.jpg' in self.avatars.objectIds())

        # users don't have an avatar image yet
        self.assertTrue(self.scott.portrait is None)
        self.assertTrue(self.john.portrait is None)

        view = ImportAvatarsView(self.avatars, self.request)
        result = view()

        # john_doe's profile name differs from the image filename
        # so he did not get a new avatar
        self.assertEquals(
            result,
            u'done 1 portraits')
        self.assertTrue(self.john.portrait is None)

        self.assertTrue(len(self.scott.portrait.data) > 0)
        self.assertEquals(self.scott.portrait.filename,
                          'scott-tiger.jpg')


class TestCSVImportView(BaseTestCase):

    def _get_fixture_location(self, name):
        return os.path.join(
            os.path.dirname(__file__),
            'fixtures',
            name)

    def _parse_file(self, filedata):
        data = tablib.Dataset()
        data.csv = filedata
        return data

    def test_validate(self):
        view = CSVImportView(self.profiles, self.request)

        missing_fields_file_loc = self._get_fixture_location(
            'core_fields_missing.csv')
        with open(missing_fields_file_loc) as mf:
            data = self._parse_file(mf.read())
        with self.assertRaises(custom_exc.MissingCoreFields):
            view.validate(data)

        user_fields_file_loc = self._get_fixture_location(
            'basic_users.csv')
        with open(user_fields_file_loc) as bf:
            self.assertTrue(
                view.validate(self._parse_file(bf.read())),
                'Validation unexpectedly failed.',
            )

        extra_fields_file_loc = self._get_fixture_location(
            'extra_column.csv')
        with open(extra_fields_file_loc) as bf:
            data = self._parse_file(bf.read())
        with self.assertRaises(custom_exc.ExtraneousFields):
            view.validate(data)

    def test_validate_extra_behaviour(self):
        """Test that if arbitrary behaviors are added to the userprofile
        type, then the validation takes this into account.
        """
        view = CSVImportView(self.profiles, self.request)
        fti = getUtility(IDexterityFTI, name=USER_PORTAL_TYPE)
        behaviors = fti.behaviors + (
            'ploneintranet.userprofile.tests.test_import.IDummySchema',)
        fti.behaviors = behaviors
        invalidate_cache(fti)

        extra_fields_file_loc = self._get_fixture_location(
            'extra_column.csv')
        with open(extra_fields_file_loc) as bf:
            self.assertTrue(
                view.validate(self._parse_file(bf.read())),
                'Validation unexpectedly failed.',
            )

    def test_create_update_users(self):
        view = CSVImportView(self.profiles, self.request)
        user_fields_file_loc = self._get_fixture_location(
            'basic_users.csv')
        with open(user_fields_file_loc) as bf:
            filedata = self._parse_file(bf.read())

        self.assertEqual(len(self.profiles.objectValues()), 0)

        count = view.create_update_users(filedata)
        self.assertEqual(count, 2)
        self.assertEqual(
            len(self.profiles.objectValues()), 2, "Users not created")

        # validation failure on duplicate username
        with self.assertRaises(custom_exc.DuplicateUser):
            view.create_update_users(filedata)

        file_loc = self._get_fixture_location(
            'missing_first_name.csv')
        with open(file_loc) as bf:
            filedata = self._parse_file(bf.read())

        # validation failure on missing required field
        with self.assertRaises(schema.interfaces.RequiredMissing):
            view.create_update_users(filedata)
        # Even though an exception was raised we will have an extra user
        # here as the transaction is handled by the process method
        self.assertEqual(
            len(self.profiles.objectValues()), 3, "Users not created")

        # now update one of the users
        user_fields_file_loc = self._get_fixture_location(
            'basic_users.csv')
        with open(user_fields_file_loc) as bf:
            filedata = self._parse_file(bf.read())
        raw = filedata.csv
        email = 'barry2@test.com'
        raw = raw.replace('barry@test.com', email)
        filedata.csv = raw

        view.create_update_users(filedata, update=True)
        self.assertEqual(
            len(self.profiles.objectValues()), 3,
            "Users not created correctly",
        )
        user = self.membrane_tool.searchResults(
            getUserId='foo')
        self.assertEqual(
            user[0].getObject().email,
            email,
            'User not updated',
        )

    def test_password_is_kept(self):
        view = CSVImportView(self.profiles, self.request)

        # if no password is provided in the import file, one get's generated
        user_fields_file_loc = self._get_fixture_location(
            'basic_users.csv')
        with open(user_fields_file_loc) as bf:
            filedata = self._parse_file(bf.read())
        view.create_update_users(filedata)

        barry = pi_api.userprofile.get('foo')
        doug = pi_api.userprofile.get('bar')
        barry_pwd = barry.password
        doug_pwd = doug.password
        # both got encrypted passwords
        self.assertTrue(barry_pwd.startswith('{BCRYPT}'))
        self.assertTrue(doug_pwd.startswith('{BCRYPT}'))
        # doug got the password provided in the import file
        self.assertTrue(
            IMembraneUserAuth(doug).verifyCredentials(
                dict(login='bar', password='my-secret!')))

        # now re-import the same users but provide a new password for barry
        user_fields_file_loc = self._get_fixture_location(
            'basic_users_password.csv')
        with open(user_fields_file_loc) as bf:
            filedata = self._parse_file(bf.read())
        view.create_update_users(filedata, update=True)

        # barry should get a new password
        self.assertNotEqual(barry_pwd, barry.password)
        self.assertTrue(
            IMembraneUserAuth(barry).verifyCredentials(
                dict(login='foo', password='updated_pwd')))
        # doug's password should still be the same
        self.assertEqual(doug_pwd, doug.password)
        # both got new surnames:
        self.assertEqual(barry.last_name, u'Whiter')
        self.assertEqual(doug.last_name, u'Carsbest')

    def test_process(self):
        view = CSVImportView(self.profiles, self.request)
        file_loc = self._get_fixture_location(
            'missing_first_name.csv')
        with open(file_loc) as bf:
            filedata = bf.read()

        view.process(filedata)
        messages = IStatusMessage(self.request)
        m = messages.show()
        self.assertEqual(
            m[0].message,
            u'Missing required field first_name on row 1'
        )

        user_fields_file_loc = self._get_fixture_location(
            'basic_users.csv')
        with open(user_fields_file_loc) as bf:
            filedata = bf.read()
        view.process(filedata)
