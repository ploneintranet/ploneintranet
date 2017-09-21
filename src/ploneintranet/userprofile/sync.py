# coding=utf-8
from .content.userprofile import IUserProfile
from .content.workgroup import IWorkGroup
from Acquisition import aq_base
from datetime import datetime
from plone import api
from plone.namedfile.file import NamedBlobImage
from plone.protect.interfaces import IDisableCSRFProtection
from ploneintranet import api as pi_api
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from Products.PluggableAuthService.interfaces.plugins import IPropertiesPlugin
from StringIO import StringIO
from transaction import commit
from zope.component import adapter
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import Interface

import logging
import time


NO_VALUE = object()
PROP_SHEET_MAP_KEY = 'ploneintranet.userprofile.property_sheet_mapping'
PRI_EXT_USERS_KEY = 'ploneintranet.userprofile.primary_external_user_source'

logger = logging.getLogger(__name__)


def purge_all_caches():
    ''' Purge everything, we want fresh data
    '''
    # purge the acl_users cache
    acl_users = api.portal.get_tool('acl_users')
    if acl_users.ZCacheable_enabled():
        acl_users.ZCacheable_invalidate()

    ldap_key = api.portal.get_registry_record(PRI_EXT_USERS_KEY)
    au = api.portal.get_tool('acl_users')
    if ldap_key not in au:
        return
    try:
        au[ldap_key].acl_users.manage_reinit()
    except AttributeError:
        logger.warning('Cannot find a specific method to purge LDAP cache')


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

    def turn_properties_plugin_on(self):
        """ Turn on properties plugin if deactivated. Returns state.
        """
        plugins = api.portal.get_tool(name='acl_users').plugins
        plugin_id = api.portal.get_registry_record(PRI_EXT_USERS_KEY)
        if not plugin_id or not getattr(plugins, plugin_id, None):
            return

        if plugin_id not in \
           [x[0] for x in plugins.listPlugins(IPropertiesPlugin)]:
            if IPropertiesPlugin.providedBy(getattr(plugins, plugin_id)):
                plugins.activatePlugin(IPropertiesPlugin, plugin_id)
                return True
        return False

    def turn_properties_plugin_off_again(self):
        """ Turns the plugin off again """
        plugins = api.portal.get_tool(name='acl_users').plugins
        plugin_id = api.portal.get_registry_record(PRI_EXT_USERS_KEY)
        if not plugin_id or not getattr(plugins, plugin_id, None):
            return

        if IPropertiesPlugin.providedBy(getattr(plugins, plugin_id)):
            plugins.deactivatePlugin(IPropertiesPlugin, plugin_id)

    def sync(self):
        was_activated = self.turn_properties_plugin_on()

        logger.info('Updating info for {0.username}'.format(self.context))
        member = api.user.get(username=self.context.username)
        if not member:
            logger.info('Cannot find {0.username}'.format(self.context))
            return

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
            value = undouble_unicode_escape(value)
            current_value = getattr(self.context, property_name, None)

            # Special handling for portraits, they need wrapping
            if property_name == 'portrait' and \
               value is not None and value is not NO_VALUE:
                current_value = self.context.portrait and \
                    self.context.portrait.data or None
                if current_value == value:
                    # profile image is the same, no need to save new image
                    continue
                value = NamedBlobImage(
                    data=value,
                    filename=u'portrait-%s.jpg' % self.context.username)

            if value is not NO_VALUE and safe_unicode(value) != current_value:
                setattr(self.context, property_name, safe_unicode(value))
                changed = True

        if changed:
            record_last_sync(self.context)
            self.context.reindexObject()
            logger.info('Properties updated for {0.username}'.format(
                self.context))
        # Turn off properties plugin again if it was deactivated
        if was_activated is True:
            self.turn_properties_plugin_off_again()


class BaseSyncView(BrowserView):
    """adds handler that stores logging information
    in a stream and adds it to the response to give
    users detailed feedback

    call with ?quiet=True to not add logging information
    """

    def __call__(self, quiet=None):
        alsoProvides(self.request, IDisableCSRFProtection)
        if quiet is None:
            quiet = self.request.get('quiet', 'False') in [
                'true', 'True', 1, '1']

        if not quiet:
            stream = StringIO()
            self.handler = logging.StreamHandler(stream)
            logger.addHandler(self.handler)

        result = self._sync() or ''

        if not quiet:
            logger.removeHandler(self.handler)
            logged = stream.getvalue()
            stream.close()
            self.request.response.setHeader('Content-type', 'text/plain')
            return result + '\n\n' + logged
        else:
            return result

    def _sync(self):
        """do the sync job and return success message as string
        """
        raise NotImplementedError()


class UserPropertySync(BrowserView):

    def __call__(self):
        """Sync a single user profile with external property providers"""
        purge_all_caches()
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
        skipped = 0
        for (count, user) in enumerate(users, start=1):
            try:
                profile_manager = IUserProfileManager(user)
            except TypeError:
                # Could not adapt: WorkspaceFolder
                skipped += 1
                continue
            profile_manager.sync()
            if count and not count % 100:
                logger.info('Synced %s profiles. Committing.', count + 1)
                commit()
        duration = time.time() - start
        logger.info('Updated {} (skipped {}) in {:0.2f} seconds'.format(
            count, skipped, duration))
    else:
        logger.info('No users to sync')


class AllUsersPropertySync(BaseSyncView):

    def _sync(self):
        """Sync properties from PAS into the membrane object for
        all users across the application.
        """
        purge_all_caches()
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
        with api.env.adopt_roles(roles=('Manager',)):
            profile = pi_api.userprofile.create(userid, approve=True)
            profile_manager = IUserProfileManager(profile)
            profile_manager.sync()


class AllUsersSync(BaseSyncView):
    """Sync all users from the "canonical" source of external users.

    Compares local membrane profiles to the list of users found
    in the canonical pas source.
    Removes any profiles for users no longer in the canonical source,
    and creates profiles for any new users found in the canonical source.
    """

    def _plugin_userids(self, plugin_id):
        acl_users = api.portal.get_tool(name='acl_users')
        return [x['id'] for x in
                acl_users[plugin_id].enumerateUsers()]

    @property
    def canonical_plugin_id(self):
        return api.portal.get_registry_record(PRI_EXT_USERS_KEY)

    def _sync(self):
        purge_all_caches()
        external_userids = set(self._plugin_userids(self.canonical_plugin_id))
        local_userids = set(self._plugin_userids('membrane_users'))
        self._disable_user_profiles(local_userids, external_userids)
        to_sync = self._create_user_profiles(local_userids, external_userids)
        sync_many(self.context, list(to_sync))
        return 'User sync complete.'

    def _create_user_profiles(self, local_userids, external_userids):
        """Create user profiles for any external user
        without a local membrane profile"""
        to_sync = external_userids - local_userids
        plugin_id = self.canonical_plugin_id
        logger.info('Found {0} users in {1} in total'.format(
            len(external_userids), plugin_id,
        ))
        logger.info('Found {0} users in {1} with no membrane profile'.format(
            len(to_sync), plugin_id,
        ))
        counter = 0
        for userid in to_sync:
            logger.info(
                'Creating profile for new user '
                'found in plugin {0}: {1}'.format(plugin_id, userid)
            )
            try:
                obj = pi_api.userprofile.create(username=userid, approve=True)
            except:
                logger.exception('Error creating: %r', userid)
                obj = None
            if obj:
                counter += 1
                if counter % 100 == 0:
                    logger.info('Created %s profiles. Committing.', counter)
                    commit()
                yield obj

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


class IWorkGroupManager(Interface):
    """Sync properties for a workgroup
    """


@adapter(IWorkGroup)
@implementer(IWorkGroupManager)
class WorkGroupPropertyManager(object):

    def __init__(self, context):
        self.context = context
        # self.property_mapping = api.portal.get_registry_record(
        #     PROP_SHEET_MAP_KEY)

    @property
    def canonical_plugin_id(self):
        return api.portal.get_registry_record(PRI_EXT_USERS_KEY)

    def sync(self):
        logger.info('Updating info for {0.id}'.format(self.context))
        changed = False
        acl_users = api.portal.get_tool(name='acl_users')
        ext_source = acl_users[self.canonical_plugin_id]
        groups = ext_source.enumerateGroups(id=self.context.canonical,
                                            exact_match=True)
        if len(groups) != 1:
            return
        group = groups[0]

        def safe_set(data, key):
            value = safe_unicode(data.get(key, ''))
            if data.get(key) and value != getattr(self.context, key):
                setattr(self.context, key, data[key])
                return True
            return False

        for key in ('title', 'description', 'mail'):
            changed = changed or safe_set(group, key)

        members = ext_source.getGroupMembers(self.context.canonical)
        if set(members) != set(self.context.members):
            # Make sure all members are unicode
            # AD allows unicode uids, we don't, and we break otherwise if such
            # are included.
            umembers = set([safe_unicode(x) for x in members])
            self.context.members = umembers
            changed = True

        if changed:
            record_last_sync(self.context)
            self.context.reindexObject()
            logger.info('Properties updated for {0.id}'.format(
                self.context))


class WorkGroupPropertySync(BrowserView):

    def __call__(self):
        """Sync a single user profile with external property providers"""
        purge_all_caches()
        alsoProvides(self.request, IDisableCSRFProtection)
        group = self.context
        IWorkGroupManager(group).sync()
        api.portal.show_message(message=_('WorkGroup property sync complete.'),
                                request=self.request)
        return self.request.response.redirect(group.absolute_url())


def sync_many_groups(group_container, groups):
    if groups:
        start = time.time()
        record_last_sync(group_container)
        skipped = 0
        for (count, group) in enumerate(groups, start=1):
            try:
                profile_manager = IWorkGroupManager(group)
            except TypeError:
                # Could not adapt: Group
                skipped += 1
                continue
            profile_manager.sync()
            if count and not count % 100:
                logger.info('Synced %s groups. Committing.', count + 1)
                commit()
        duration = time.time() - start
        logger.info('Updated {} (skipped {}) in {:0.2f} seconds'.format(
            count, skipped, duration))
    else:
        logger.info('No groups to sync')


class AllWorkGroupsSync(BaseSyncView):
    """Sync all groups from the "canonical" source of external groups.

    Compares local membrane groups to the list of groups found
    in the canonical pas source.
    Removes any groups no longer in the canonical source,
    and creates groups for any new groups found in the canonical source.
    """

    def get_groups_container(self):
        container = 'groups'
        portal = api.portal.get()
        if container not in portal:
            groups_container = api.content.create(
                container=portal,
                type='ploneintranet.workspace.workspacecontainer',
                title='WorkGroups'
            )
        else:
            groups_container = portal[container]

        return groups_container

    def _plugin_groupids(self, plugin_id):
        acl_users = api.portal.get_tool(name='acl_users')
        plugin = acl_users[plugin_id]
        if plugin_id != 'membrane_groups':
            return [x['id'] for x in plugin.enumerateGroups()]
        groups_container = self.get_groups_container()
        return [
            x.canonical for x in groups_container.objectValues()
        ]

    @property
    def canonical_plugin_id(self):
        return api.portal.get_registry_record(PRI_EXT_USERS_KEY)

    def _sync(self):
        purge_all_caches()
        external_groupids = set(self._plugin_groupids(
            self.canonical_plugin_id))
        local_groupids = set(self._plugin_groupids('membrane_groups'))
        self._disable_groups(local_groupids, external_groupids)
        # _create_groups is unfortunately a generator, so we need to consume it
        tuple(self._create_groups(local_groupids, external_groupids))
        sync_many_groups(self.context, self.context.objectValues())
        return 'Group sync complete.'

    def _create_groups(self, local_groupids, external_groupids):
        """Create user profiles for any external user
        without a local membrane profile"""
        to_sync = external_groupids - local_groupids
        plugin_id = self.canonical_plugin_id
        logger.info('Found {0} workgroups in {1} in total'.format(
            len(external_groupids), plugin_id,
        ))
        logger.info('Found {0} workgroups in {1} with no membrane profile'
                    .format(len(to_sync), plugin_id,))
        counter = 0
        for groupid in to_sync:
            logger.info(
                'Creating new workgroup '
                'found in plugin {0}: {1}'.format(plugin_id, groupid)
            )
            try:
                obj = pi_api.workgroup.create(groupid=groupid)
            except:
                logger.exception('Error creating: %r', groupid)
                obj = None
            if obj:
                counter += 1
                if counter % 100 == 0:
                    logger.info('Created %s workgroups. Committing.', counter)
                    commit()
                yield obj

    def _disable_groups(self, local_groupids, external_groupids):
        """Disable groups for any that are missing
        a corresponding external group."""
        to_remove = local_groupids - external_groupids
        plugin_id = self.canonical_plugin_id
        for groupid in to_remove:
            group = api.group.get(groupid)
            if not group:
                continue
            profile = self.context[group.getProperty('object_id')]
            # Only disable our WorkGroup type.
            # Don't do that with groupspaces or others
            if profile.portal_type != 'ploneintranet.userprofile.workgroup':
                continue
            state = api.content.get_state(obj=profile)
            # Skip users that have never been synced with an external source
            # as they were probably created manually
            if state == 'enabled' and get_last_sync(profile) is not None:
                logger.info(
                    'Disabling workgroup '
                    'no longer in plugin {0}: {1}'.format(
                        plugin_id,
                        groupid,
                    )
                )
                api.content.transition(obj=self.context[groupid],
                                       transition='disable')


def undouble_unicode_escape(value):
    """Work around a unicode bug somewhere in the PloneLDAP stack
    that results in some values being doubly unicode encoded.
    """
    if isinstance(value, str):
        return value
    try:
        # doubly escaped
        return value.encode('raw_unicode_escape').decode('utf-8')
    except UnicodeDecodeError:
        # normal unicode
        return value
    except Exception:
        # object, whatever
        return value
