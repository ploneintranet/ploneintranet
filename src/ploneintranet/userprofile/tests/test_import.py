import os
from ploneintranet.userprofile.tests.base import BaseTestCase
from ploneintranet.userprofile.browser.user_import import CSVImportView


class TestCSVImportView(BaseTestCase):

    def test_validate(self):
        view = CSVImportView(self.profiles, self.request)

        missing_fields_file_loc = os.path.join(
            os.path.dirname(__file__),
            'fixtures',
            'core_fields_missing.csv')
        with open(missing_fields_file_loc) as mf:
            self.assertFalse(
                view.validate(mf.read()),
                'Validation unexpectedly passed.',
            )

        missing_fields_file_loc = os.path.join(
            os.path.dirname(__file__),
            'fixtures',
            'basic_users.csv')
        with open(missing_fields_file_loc) as bf:
            self.assertTrue(
                view.validate(bf.read()),
                'Validation unexpectedly failed.',
            )
