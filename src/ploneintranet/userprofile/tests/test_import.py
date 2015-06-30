import os
import tablib

from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.schema import invalidate_cache
from plone.directives import form
from ploneintranet.userprofile.browser.user_import import CSVImportView
from ploneintranet.userprofile.browser.user_import import USER_PORTAL_TYPE
from ploneintranet.userprofile.tests.base import BaseTestCase
from zope import schema
from zope.component import getUtility
from zope.interface import alsoProvides


class IDummySchema(form.Schema):

    hair_colour = schema.TextLine(
        title=u'Hair colour')
alsoProvides(IDummySchema, IFormFieldProvider)


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
            self.assertFalse(
                view.validate(self._parse_file(mf.read())),
                'Validation unexpectedly passed.',
            )

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
            self.assertFalse(
                view.validate(self._parse_file(bf.read())),
                'Validation unexpectedly passed.',
            )

    def test_validate_extra_behaviour(self):
        """Test that if arbitrary behaviors are added to the userprofile
        type, then the validation takes this into account.
        """
        view = CSVImportView(self.profiles, self.request)
        fti = getUtility(IDexterityFTI, name=USER_PORTAL_TYPE)
        behaviors = fti.behaviors + (
            'ploneintranet.userprofile.tests.test_import.IDummySchema', )
        fti.behaviors = behaviors
        invalidate_cache(fti)
        fti.__dict__.pop('_v_schema_behavior_schema_interfaces')

        extra_fields_file_loc = self._get_fixture_location(
            'extra_column.csv')
        with open(extra_fields_file_loc) as bf:
            self.assertTrue(
                view.validate(self._parse_file(bf.read())),
                'Validation unexpectedly failed.',
            )

    def test_create_users(self):
        view = CSVImportView(self.profiles, self.request)
        user_fields_file_loc = self._get_fixture_location(
            'basic_users.csv')
        with open(user_fields_file_loc) as bf:
            filedata = self._parse_file(bf.read())

        self.assertEqual(len(self.profiles.objectValues()), 0)

        view.create_users(filedata)
        self.assertEqual(
            len(self.profiles.objectValues()), 2, "Users not created")
