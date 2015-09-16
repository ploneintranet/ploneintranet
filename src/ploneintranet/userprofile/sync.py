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

from ploneintranet import api as pi_api
from ploneintranet.core import ploneintranetCoreMessageFactory as _  # noqa
from .content.userprofile import IUserProfile


NO_VALUE = object()
PROP_SHEET_MAP_KEY = 'ploneintranet.userprofile.property_sheet_mapping'
PRI_EXT_USERS_KEY = 'ploneintranet.userprofile.primary_external_user_source'

logger = logging.getLogger(__name__)


def record_last_sync(context):
    context.last_sync = datetime.utcnow()


def get_last_sync(context):
    return getattr(context, 'last_sync', None)


class IUserProfileManager(Interface):
    """Sync properties for a user profile
    """


@adapter(IUserProfile)
@implementer(IUserProfileManager)
class UserPropertyManager(object):

    def __init__(self, context):
        self.context = context
        self.property_mapping = api.portal.get_registry_record(
            PROP_SHEET_MAP_KEY)

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


def sync_many(profiles_container, users):
    if users:
        start = time.time()
        record_last_sync(profiles_container)
        for (count, user) in enumerate(users, start=1):
            profile_manager = IUserProfileManager(user)
            profile_manager.sync()
        duration = time.time() - start
        logger.info('Updated {} in {:0.2f} seconds'.format(count, duration))
    else:
        logger.info('No users to sync')


class AllUsersPropertySync(BrowserView):

    def __call__(self):
        """Sync properties from PAS into the membrane object for
        all users across the application.
        """
        alsoProvides(self.request, IDisableCSRFProtection)

        users = self._get_users_to_sync()
        sync_many(self.context, users)

    def _get_users_to_sync(self):
        """Override this to specify a subset of users to
        be updated.
        """
        membrane = api.portal.get_tool(name='membrane_tool')
        for brain in membrane.searchResults():
            yield brain.getObject()


def create_membrane_profile(member):
    userid = member.getId()
    membrane_user = pi_api.userprofile.get(userid)
    if membrane_user is None:
        logger.info('Auto-creating membrane profile for {0}'.format(
            userid,
        ))
        with api.env.adopt_roles(roles=('Manager', )):
            profile = pi_api.userprofile.create(userid, approve=True)
            profile_manager = IUserProfileManager(profile)
            profile_manager.sync()


class AllUsersSync(BrowserView):
    """Sync all users from the "canonical" source of external users."""

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        self._sync()

    def _sync(self):
        pas_plugin_id = api.portal.get_registry_record(PRI_EXT_USERS_KEY)
        acl_users = api.portal.get_tool(name='acl_users')
        external_userids = set(acl_users[pas_plugin_id].getUserIds())
        local_userids = set(acl_users['membrane_users'].getUserIds())
        self._delete_user_profiles(local_userids, external_userids)
        to_sync = self._create_user_profiles(local_userids, external_userids)
        sync_many(self.context, list(to_sync))

    def _create_user_profiles(self, local_userids, external_userids):
        to_sync = external_userids - local_userids
        for userid in to_sync:
            yield pi_api.userprofile.create(username=userid)

    def _delete_user_profiles(self, local_userids, external_userids):
        to_remove = local_userids - external_userids
        plugin_id = self.canonical_plugin_id
        for userid in to_remove:
            logger.info(
                'Disabling profile for user '
                'no longer in plugin {0}: {1}'.format(
                    plugin_id,
                    userid,
                )
            )
            profile = self.context[userid]
            if api.content.get_state(obj=profile) == 'enabled':
                api.content.transition(obj=self.context[userid],
                                       transition='disable')
