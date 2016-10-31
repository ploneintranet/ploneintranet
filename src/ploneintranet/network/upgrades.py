# coding=utf-8
from BTrees.OOBTree import OOBTree
from datetime import datetime
from logging import getLogger
from plone import api
from ploneintranet.layout.setuphandlers import create_apps
import pytz

default_profile = 'profile-ploneintranet.network:default'
logger = getLogger(__name__)


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


def upgrade_to_0005(context):
    ''' Apps are now objects, so we want to update the bookmark storage
    '''
    ng = api.portal.get_tool('ploneintranet_network')
    # We have some bookmarked apps as paths
    paths = set(ng._bookmarked.get('apps'))

    # and we now have some apps
    create_apps()
    portal = api.portal.get()
    apps = [app for app in portal.apps.objectValues() if app.app]

    # We want to create a mapping between those ones
    mapping = {}
    for path in paths:
        for app in apps:
            if app.app in path:
                mapping[path] = app.UID()
                logger.info(
                    'Mapping path %s to application %s (%s)',
                    path,
                    app.title.encode('utf8'),
                    app.UID(),
                )

    # If there are some differences, warn the user
    for path in paths.difference(mapping):
        logger.warning(
            'Cannot map path %s to any of %r',
            path,
            sorted([app.app for app in apps])
        )

    # Now we migrate the database
    for path in mapping:
        uid = mapping[path]
        users = ng._bookmarked['apps'].pop(path, [])
        for user in users:
            # If the app is not already bookmarked for some reason,
            # bookmark it
            if not ng.is_bookmarked('content', uid, user):
                ng.bookmark('content', uid, user)
                # but setting an older timestamp (if possible)
                old_date = ng._bookmarked_on[user].pop(path, None)
                if old_date:
                    ng._bookmarked_on[user][uid] = old_date
            # At this point we also clear the bookmarks
            try:
                ng._bookmarks['apps'][user].remove(path)
            except KeyError:
                logger.info(
                    'User %s bookmark %s appears already removed',
                    user,
                    path,
                )

    # Finally clean up keys with empty values
    for user in set(ng._bookmarks.get('apps', [])):
        if not ng._bookmarks['apps'][user]:
            ng._bookmarks['apps'].pop(user)

    if not ng._bookmarks.get('apps'):
        ng._bookmarks.pop('apps', None)
    if not ng._bookmarked.get('apps'):
        ng._bookmarked.pop('apps', None)
