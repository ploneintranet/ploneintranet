# coding=utf-8
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
