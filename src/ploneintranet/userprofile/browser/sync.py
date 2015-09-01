import logging
import time

from Products.Five import BrowserView
from plone import api
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface

from ..content.userprofile import IUserProfile


class IUserProfileManager(Interface):
    """Sync properties for a user profile
    """

_no_value = object()
logger = logging.getLogger(__name__)


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
        membrane_properties = property_sheet_mapping.pop('membrane_properties')
        changed = False
        for (property_name, pas_plugin_id) in self.property_mapping.items():
            sheet = property_sheet_mapping[pas_plugin_id]
            value = sheet.getProperty(property_name, default=_no_value)
            if value is not _no_value:
                membrane_properties.setProperty(member, property_name, value)
                changed = True

        if changed:
            self.context.reindexObject()


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
        start = time.time()
        for (count, user) in enumerate(self._get_users_to_sync(), start=1):
            IUserProfileManager(user).sync()
        duration = time.time() - start
        logger.info('Updated {} in {:0.2f} seconds'.format(
            count, duration))
