# coding=utf-8
from ploneintranet.notifications.queue import AppendableLOBTree
from logging import getLogger
from persistent.list import PersistentList
from plone import api

logger = getLogger(__name__)


def switch_to_lobtrees(self):
    ''' The ploneintranet_notifications tool should use LOBtrees
    instead of PersistentLists
    '''
    pn = api.portal.get_tool('ploneintranet_notifications')
    keys = sorted(pn._users.keys())
    for key in keys:
        values = pn._users.get(key, [])
        if isinstance(values, PersistentList):
            logger.info(
                'Fixing %s queued values for user %s',
                len(values),
                key,
            )
            pn._users[key] = AppendableLOBTree()
            for value in values:
                pn.append_to_user_queue(key, value)
