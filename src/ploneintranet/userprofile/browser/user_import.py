import tablib

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import getUtility


USER_PORTAL_TYPE = "ploneintranet.userprofile.userprofile"


class CSVImportView(BrowserView):
    """Add user profiles based on a supplied csv"""

    index = ViewPageTemplateFile('templates/user_import_form.pt')

    def __call__(self):
        return self.index()

    def _normalise_headers(self, headers):
        """Allow column headings to contain spaces etc.
        :type headers: list
        """
        return [x.strip().lower().replace(' ', '_') for x in headers]

    def validate(self, filedata):
        """
        Validates the file's column headers.

        :rtype: bool

        * Validates that core required fields are present
        (ploneintranet.userprofile.content.userprofile.IUserProfile)
        * Supports other fields that exist via (optional) dx behaviours
        """
        data = tablib.Dataset()
        data.csv = filedata

        # check for core user fields
        fti = getUtility(IDexterityFTI, name=USER_PORTAL_TYPE)
        core_user_fields = set(fti.lookupSchema().names())
        core_user_fields.remove('portrait')  # Makes no sense for csv import
        headers = set(self._normalise_headers(data.headers))
        if not core_user_fields <= headers:
            return False

        return True
