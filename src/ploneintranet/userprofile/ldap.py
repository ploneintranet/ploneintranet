"""
LDAP/AD-specific support for user property syncing
"""
import logging

from plone.app.ldap.ploneldap.util import getLDAPPlugin
from plone import api
from .sync import AllUsersPropertySync
from .sync import get_last_sync

logger = logging.getLogger(__name__)

# TODO: Make this configurable
LDAP_CHANGED_ATTRIBUTE = 'whenChanged'


class LDAPChangedUsersPropertySync(AllUsersPropertySync):

    def _get_users_to_sync(self):
        """Perform a custom LDAP query to limit the users
        who should be updated.

        Looks for users that have changed since the last sync,
        according to the LDAP_CHANGED_ATTRIBUTE

        (Requires plone.app.ldap)
        """
        last_sync = get_last_sync(self.context)
        if not last_sync:
            # First sync is always a full sync
            return super(LDAPChangedUsersPropertySync,
                         self)._get_users_to_sync()

        logger.info('Looking for LDAP users changed since {0}'.format(
            last_sync,
        ))

        try:
            ldap_plugin = getLDAPPlugin()
        except KeyError:
            logger.error('No LDAP plugin found!')
            return []

        ldap_folder = ldap_plugin['acl_users']

        # Convert to AD/LDAP date string
        datestring = last_sync.strftime('%Y%m%d%H%M%S.0Z')
        changed_filter = '({0}>={1})'.format(
            LDAP_CHANGED_ATTRIBUTE,
            datestring,
        )
        # Combine date check with the default LDAP filters
        search_str = ldap_folder._getUserFilterString(
            filters=(changed_filter,)
        )

        # Perform a search using the LDAPUserFolder
        login_attr = ldap_folder._login_attr
        results = ldap_folder._delegate.search(
            base=ldap_folder.users_base,
            scope=ldap_folder.users_scope,
            filter=search_str,
            attrs=(login_attr, ),
        )
        if results['exception']:
            logger.debug('Error in ldap query (%s)' % results['exception'])
            return []
        if results['size'] == 0:
            logger.info('No users to update')
            return []

        # Translate to membrane profiles
        userids = [x[login_attr][0] for x in results['results']]
        mtool = api.portal.get_tool('membrane_tool')
        users = mtool.searchResults(exact_getUserId=userids)
        logger.info('Found {0} users to update from LDAP'.format(
            len(users)
        ))
        return [user.getObject() for user in users]
