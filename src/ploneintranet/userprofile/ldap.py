import logging

from plone.app.ldap.ploneldap.util import getLDAPPlugin
from plone import api
from .sync import AllUsersPropertySync
from .sync import get_last_sync

logger = logging.getLogger(__name__)


class LDAPChangedUsersPropertySync(AllUsersPropertySync):

    def _get_users_to_sync(self):
        """Perform a custom LDAP query to limit the users
        who should be updated.

        Looks for users with a 'whenChanged' value

        Requires plone.app.ldap
        """
        last_sync = get_last_sync(self.context)
        if not last_sync:
            # Never been synced - so sync all current membrane profiles
            return super(LDAPChangedUsersPropertySync,
                         self)._get_users_to_sync()

        try:
            ldap_plugin = getLDAPPlugin()
        except KeyError:
            logger.error('No LDAP plugin found!')
            return []

        ldap_folder = ldap_plugin['acl_users']
        login_attr = ldap_folder._login_attr
        datestring = last_sync.strftime('%Y%m%d%H%M%S.0Z')
        logger.info('Looking for LDAP users changed since {0}'.format(
            last_sync,
        ))

        changed_filter = '(whenChanged>={0})'.format(datestring)
        search_str = ldap_folder._getUserFilterString(
            filters=(changed_filter,))

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

        userids = [x[login_attr][0] for x in results['results']]
        mtool = api.portal.get_tool('membrane_tool')
        users = mtool.searchResults(exact_getUserId=userids)
        logger.info('Found {0} users to update from LDAP'.format(
            len(users)
        ))
        return [user.getObject() for user in users]
