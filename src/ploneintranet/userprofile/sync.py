import logging
import time
from datetime import datetime

from Products.Five import BrowserView
from plone import api
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import alsoProvides
from plone.protect.interfaces import IDisableCSRFProtection

from ploneintranet.core import ploneintranetCoreMessageFactory as _  # noqa
from .content.userprofile import IUserProfile


class IUserProfileManager(Interface):
    """Sync properties for a user profile
    """

NO_VALUE = object()
logger = logging.getLogger(__name__)


def record_last_sync(context):
    context.last_sync = datetime.utcnow()


@adapter(IUserProfile)
@implementer(IUserProfileManager)
class UserPropertyManager(object):

    def __init__(self, context):
        self.context = context
        self.property_mapping = api.portal.get_registry_record(
            'ploneintranet.userprofile.property_sheet_mapping')

    def sync(self):
        logger.info('Updating info for {0.username}'.format(self.context))
        member = api.user.get(username=self.context.username)
        property_sheet_mapping = {
            sheet.getId(): sheet
            for sheet in member.getOrderedPropertySheets()
        }
        changed = False
        for (property_name, pas_plugin_id) in self.property_mapping.items():
            if pas_plugin_id not in property_sheet_mapping:
                continue
            sheet = property_sheet_mapping[pas_plugin_id]
            value = sheet.getProperty(property_name, default=NO_VALUE)
            current_value = getattr(self.context, property_name)
            if value is not NO_VALUE and value != current_value:
                setattr(self.context, property_name, value)
                changed = True

        if changed:
            record_last_sync(self.context)
            self.context.reindexObject()
            logger.info('Properties updated for {0.username}'.format(
                self.context))


class UserPropertySync(BrowserView):

    def __call__(self):
        """Sync a single user profile with external property providers"""
        alsoProvides(self.request, IDisableCSRFProtection)
        userprofile = self.context
        IUserProfileManager(userprofile).sync()
        api.portal.show_message(message=_('External property sync complete.'),
                                request=self.request)
        return self.request.response.redirect(userprofile.absolute_url())


class AllUsersPropertySync(BrowserView):

    def _get_users_to_sync(self):
        """Override this to specify a subset of users to
        be updated.
        """
        membrane = api.portal.get_tool('membrane_tool')
        for brain in membrane.searchResults():
            yield brain.getObject()

    def __call__(self):
        """Sync properties from PAS into the membrane object for
        all users across the application.
        """
        alsoProvides(self.request, IDisableCSRFProtection)
        start = time.time()
        for (count, user) in enumerate(self._get_users_to_sync(), start=1):
            IUserProfileManager(user).sync()

        # set the last sync date on the userprofile container
        record_last_sync(self.context)

        duration = time.time() - start
        logger.info('Updated {} in {:0.2f} seconds'.format(
            count, duration))
