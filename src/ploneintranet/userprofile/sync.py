import logging
import time
from datetime import datetime

from Acquisition import aq_base
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
    return getattr(aq_base(context), 'last_sync', None)


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
        return 'Property sync complete.'

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
    """Sync all users from the "canonical" source of external users.

    Compares local membrane profiles to the list of users found
    in the canonical pas source.
    Removes any profiles for users no longer in the canonical source,
    and creates profiles for any new users found in the canonical source.
    """

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        self._sync()
        return 'User sync complete.'

    def _plugin_userids(self, plugin_id):
        acl_users = api.portal.get_tool(name='acl_users')
        return [x['id'] for x in
                acl_users[plugin_id].enumerateUsers()]

    @property
    def canonical_plugin_id(self):
        return api.portal.get_registry_record(PRI_EXT_USERS_KEY)

    def _sync(self):
        external_userids = set(self._plugin_userids(self.canonical_plugin_id))
        local_userids = set(self._plugin_userids('membrane_users'))
        self._disable_user_profiles(local_userids, external_userids)
        to_sync = self._create_user_profiles(local_userids, external_userids)
        sync_many(self.context, list(to_sync))

    def _create_user_profiles(self, local_userids, external_userids):
        """Create user profiles for any external user
        without a local membrane profile"""
        to_sync = external_userids - local_userids
        plugin_id = self.canonical_plugin_id
        logger.info('Found {0} users in {1} with no membrane profile'.format(
            len(to_sync), plugin_id,
        ))
        for userid in to_sync:
            logger.info(
                'Creating profile for new user '
                'found in plugin {0}: {1}'.format(plugin_id, userid)
            )
            yield pi_api.userprofile.create(username=userid, approve=True)

    def _disable_user_profiles(self, local_userids, external_userids):
        """Disable user profiles for any that are missing
        a corresponding external user."""
        to_remove = local_userids - external_userids
        plugin_id = self.canonical_plugin_id
        for userid in to_remove:
            profile = self.context[userid]
            state = api.content.get_state(obj=profile)
            # Skip users that have never been synced with an external source
            # as they were probably created manually
            if state == 'enabled' and get_last_sync(profile) is not None:
                logger.info(
                    'Disabling profile for user '
                    'no longer in plugin {0}: {1}'.format(
                        plugin_id,
                        userid,
                    )
                )
                api.content.transition(obj=self.context[userid],
                                       transition='disable')
