import tablib

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from ploneintranet import api as pi_api
from ploneintranet.userprofile import _
from ploneintranet.userprofile import exc as custom_exc
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import getAdditionalSchemata
from zope.component import getUtility
from zope import schema


USER_PORTAL_TYPE = "ploneintranet.userprofile.userprofile"


class CSVImportView(BrowserView):
    """Add user profiles based on a supplied csv"""

    index = ViewPageTemplateFile('templates/user_import_form.pt')

    def __call__(self):
        if 'csvfile' in self.request.form:
            self.process(self.request.form.get('csvfile').read())

        return self.index()

    @property
    def core_user_schema(self):
        fti = getUtility(IDexterityFTI, name=USER_PORTAL_TYPE)
        return fti.lookupSchema()

    @property
    def user_schemata(self):
        """Includes any behaviours that have been added"""
        schematas = [self.core_user_schema]
        for behavior_schema in getAdditionalSchemata(
                portal_type=USER_PORTAL_TYPE):
            schematas.append(behavior_schema)
        return schematas

    def _normalise_key(self, key):
        return key.strip().lower().replace(' ', '_')

    def _normalise_headers(self, headers):
        """Allow column headings to contain spaces etc.
        Override this method if there is more complex csv
        column heading mapping/transformation you would like to perform.

        :type headers: list
        """
        return map(self._normalise_key, headers)

    def _show_message_redirect(self, message):
        """Convenience wrapper method for plone.api.portal.show_message
        """
        api.portal.show_message(
            message=message,
            request=self.request,
            type='error',
        )
        return self._redirect()

    def _redirect(self):
        return self.request.response.redirect(
            '{0}/{1}'.format(
                self.context.absolute_url(),
                self.__name__,
            ))

    def process(self, csvfile):
        """Process the input file, validate and
        create the users.
        """
        filedata = csvfile  # XXX This should parse the file
        data = tablib.Dataset()
        data.csv = filedata

        try:
            self.validate(data)
        except custom_exc.MissingCoreFields as e:
            return self._show_message_redirect(_(e.message))
        except custom_exc.ExtraneousFields as e:
            return self._show_message_redirect(_(e.message))

        try:
            self.create_users(data)
        except custom_exc.RequiredMissing as e:
            message = _(
                u"Missing required field {} on row {}".format(
                    e.message, e.details['row'])
            )
            return self._show_message_redirect(message)
        except custom_exc.ConstraintNotSatisfied as e:
            message = _(
                u"Constraint not satisfied for {} at row {}.".format(
                    e.details['field'], e.details['row'])
            )
            return self._show_message_redirect(message)
        except custom_exc.WrongType as e:
            message = _(
                u"Wrong type for {} at row {}.".format(
                    e.details['field'], e.details['row'])
            )
            return self._show_message_redirect(message)
        else:
            api.portal.show_message(
                message=_(u"Created XXX users"),
                request=self.request)
            return self._redirect()

    def validate(self, filedata):
        """
        Validates the file's column headers.

        :rtype: bool
        """
        # check for core user fields
        core_user_fields = set(self.core_user_schema.names())
        core_user_fields.remove('portrait')  # Makes no sense for csv import
        headers = set(self._normalise_headers(filedata.headers))
        if not core_user_fields <= headers:
            missing = core_user_fields - headers
            raise custom_exc.MissingCoreFields(
                u"The core required fields appear to be missing: {}".format(
                    ', '.join(missing)),
            )

        # check all columns in csv are used
        additional_fields = []
        for behavior_schema in getAdditionalSchemata(
                portal_type=USER_PORTAL_TYPE):
            additional_fields.extend(behavior_schema.names())
        all_user_fields = set()
        all_user_fields |= set(additional_fields)
        all_user_fields |= core_user_fields
        if not headers <= all_user_fields:
            raise custom_exc.ExtraneousFields(
                u"There are extraneous fields in the input file.",
            )

        return True

    def create_users(self, filedata):
        """Create the userprofiles.

        :param filedata: csv binary data
        :type filedata: str
        """
        # Create a mapping of field_name to schema field object.
        # This can then be used for validation
        field_mapping = {}
        for user_schema in self.user_schemata:
            for name in schema.getFieldNames(user_schema):
                field_mapping[name] = user_schema[name]

        for row, user_info in enumerate(filedata.dict):
            normalized_info = {}
            offset_row = row + 1
            for key, value in user_info.items():
                normalized_key = self._normalise_key(key)
                field = field_mapping[normalized_key]
                if not value:
                    value = None

                try:
                    field.validate(value)
                except schema.interfaces.RequiredMissing as e:
                    raise custom_exc.RequiredMissing(
                        e.message,
                        details={'row': offset_row})
                except schema.interfaces.ConstraintNotSatisfied as e:
                    raise custom_exc.ConstraintNotSatisfied(
                        e.message,
                        details={'row': offset_row, 'field': key})
                except schema.interfaces.WrongType as e:
                    raise custom_exc.WrongType(
                        e.message,
                        details={'row': offset_row, 'field': key})
                else:
                    normalized_info[normalized_key] = value

            username = normalized_info.pop('username')
            email = normalized_info.pop('email')
            pi_api.userprofile.create(username=username,
                                      email=email,
                                      properties=normalized_info)
