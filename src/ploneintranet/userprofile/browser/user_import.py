# -*- coding: utf-8 -*-
"""View for creating/updating users from an input file"""

import tablib
import itertools
import logging
import transaction

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from ploneintranet import api as pi_api
from ploneintranet.core import ploneintranetCoreMessageFactory as _  # noqa
from ploneintranet.userprofile import exc as custom_exc
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import getAdditionalSchemata
from zope.component import getUtility
from zope import schema


USER_PORTAL_TYPE = "ploneintranet.userprofile.userprofile"
logger = logging.getLogger(__name__)


class CSVImportView(BrowserView):
    """Add user profiles based on a supplied csv"""

    index = ViewPageTemplateFile('templates/user_import_form.pt')

    def __call__(self):
        form = self.request.form
        if 'csvfile' in form:
            update_existing = bool(form.get('update-existing'))
            self.process(form.get('csvfile').read(), update=update_existing)

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

    def available_field_names(self):
        """Get a full list of available field names"""
        names = [x.names() for x in self.user_schemata]
        fields = list(itertools.chain.from_iterable(names))
        fields.append('password')
        return fields

    def _normalise_key(self, key):
        return key.strip().lower().replace(' ', '_')

    def _normalise_headers(self, headers):
        """Allow column headings to contain spaces etc.
        Override this method if there is more complex csv
        column heading mapping/transformation you would like to perform.

        :type headers: list
        """
        return map(self._normalise_key, headers)

    def _redirect(self):
        return self.request.response.redirect(
            '{0}/{1}'.format(
                self.context.absolute_url(),
                self.__name__,
            ))

    def _show_message_redirect(self, message):
        """Convenience wrapper method for plone.api.portal.show_message
        """
        api.portal.show_message(
            message=message,
            request=self.request,
            type='error',
        )
        return self._redirect()

    def process(self, csvfile, update=False):
        """Process the input file, validate and
        create the users.
        """
        data = tablib.Dataset()
        try:
            data.csv = csvfile
        except tablib.core.InvalidDimensions:
            return self._show_message_redirect(
                _("File incorrectly formatted.")
            )

        try:
            self.validate(data)
        except custom_exc.MissingCoreFields as e:
            return self._show_message_redirect(_(e.message))
        except custom_exc.ExtraneousFields as e:
            return self._show_message_redirect(_(e.message))
        except tablib.core.HeadersNeeded as e:
            return self._show_message_redirect(_(e.message))

        message_type = 'error'
        try:
            count = self.create_update_users(data, update)
        except custom_exc.DuplicateUser as e:
            message = _(
                u"{} on row {}".format(
                    e.message, e.details['row'])
            )
        except custom_exc.RequiredMissing as e:
            message = _(
                u"Missing required field {} on row {}".format(
                    e.message, e.details['row'])
            )
        except custom_exc.ConstraintNotSatisfied as e:
            message = _(
                u"Constraint not satisfied for {} at row {}.".format(
                    e.details['field'], e.details['row'])
            )
        except custom_exc.WrongType as e:
            message = _(
                u"Wrong type for {} at row {}.".format(
                    e.details['field'], e.details['row'])
            )
        else:
            message_type = 'info'
            verb = update and "Updated" or "Created"
            message = _(u"{} user(s) {}.".format(count, verb))

        if message_type == 'error':
            transaction.abort()

        api.portal.show_message(
            message=message,
            request=self.request,
            type=message_type,
        )
        return self._redirect()

    def validate(self, filedata):
        """
        Validates the file's column headers.

        :rtype: bool
        """
        # check for core user fields
        required_core_user_fields = set(
            [x.getName() for x in
             schema.getFields(self.core_user_schema).values()
             if x.required]
        )

        file_headers = filedata.headers
        if not file_headers:
            raise tablib.core.HeadersNeeded('No header row found')
        headers = set(self._normalise_headers(file_headers))

        if not required_core_user_fields <= headers:
            missing = required_core_user_fields - headers
            raise custom_exc.MissingCoreFields(
                u"The following required fields are missing: {}".format(
                    ', '.join(missing)),
            )

        # check all columns in csv are used
        # (password is a special case hidden from edit schematas
        #  so we include it manually here)
        additional_fields = ['password', ]
        for behavior_schema in getAdditionalSchemata(
                portal_type=USER_PORTAL_TYPE):
            additional_fields.extend(behavior_schema.names())
        all_user_fields = set()
        all_user_fields |= set(additional_fields)
        all_user_fields |= required_core_user_fields
        if not headers <= all_user_fields:
            extra = headers - all_user_fields
            raise custom_exc.ExtraneousFields(
                u"There are extraneous fields in the input file: {0}".format(
                    ', '.join(extra),
                ),
            )

        return True

    def schema_field_mapping(self):
        """Create a mapping of field_name to schema field object.
        This can then be used for validation
        """
        field_mapping = {}
        for user_schema in self.user_schemata:
            for name in schema.getFieldNames(user_schema):
                field_mapping[name] = user_schema[name]
        return field_mapping

    def validate_field_value(self, key, value, offset_row):
        """
        """
        field_mapping = self.schema_field_mapping()
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
            return (normalized_key, value)

    def create_update_users(self, filedata, update=False):
        """Create/update the userprofiles.

        :param filedata: csv binary data
        :type filedata: str
        :param update: If True, attempt to look up user first and update
        :type update: bool
        """
        count = 0

        for row, user_info in enumerate(filedata.dict):
            offset_row = row + 1

            # get the core fields (username, email, password)
            key_mapping = {x.lower().strip(): x for x in user_info.keys()}
            username = user_info.get(key_mapping['username'])
            email = user_info.get(key_mapping['email'])
            password = None
            if 'password' in key_mapping:
                password = user_info.get(key_mapping['password'])

            user = pi_api.userprofile.get(username)
            if user is None:
                user = pi_api.userprofile.create(
                    username=username,
                    email=email,
                    password=password,
                    approve=True,
                )
            elif user is not None and not update:
                raise custom_exc.DuplicateUser(
                    u"A user with this username already exists",
                    details={'row': offset_row})

            # update additional fields
            for key, value in user_info.items():
                try:
                    norm_key, validated_value = self.validate_field_value(
                        key,
                        value,
                        offset_row
                    )
                except custom_exc.RequiredMissing as e:
                    if update:
                        # if we're updating, we can just ignore this field
                        continue
                    else:
                        raise custom_exc.RequiredMissing(
                            e.message,
                            details={'row': offset_row, 'field': key})
                if any([norm_key == 'username',
                        not update and norm_key in {'email', 'password'}]):
                    continue
                setattr(user, norm_key, validated_value)

            count += 1

        return count
