# coding=utf-8
from datetime import datetime
import pytz
from plone import api
from BTrees.OOBTree import OOBTree

default_profile = 'profile-ploneintranet.network:default'


def upgrade_to_0002(context):
    context.runImportStepFromProfile(default_profile, 'componentregistry')


def upgrade_to_0003(context):
    ''' Get the ploneintranet_network tool and make it bookmark aware
    '''
    ng = api.portal.get_tool('ploneintranet_network')
    if not hasattr(ng, '_bookmarks'):
        ng._bookmarks = OOBTree()
    if not hasattr(ng, '_bookmarked'):
        ng._bookmarked = OOBTree()

    for item_type in ng.supported_bookmark_types:
        ng._bookmarks.insert(item_type, OOBTree())
        ng._bookmarked.insert(item_type, OOBTree())


def upgrade_to_0004(context):
    ''' Set timestamps on bookmarks
    '''
    ng = api.portal.get_tool('ploneintranet_network')
    if not hasattr(ng, '_bookmarked_on'):
        ng._bookmarked_on = OOBTree()
    for btree in ng._bookmarks.values():
        for (user_id, item_ids) in btree.items():
            _init_bookmark_on(ng, user_id, item_ids)


def _init_bookmark_on(ng, user_id, item_ids):
    # leaves existing intact
    ng._bookmarked_on.insert(user_id, OOBTree())
    for item_id in item_ids:
        if item_id not in ng._bookmarked_on[user_id].keys():
            ng._bookmarked_on[user_id][item_id] = datetime.now(pytz.utc)
