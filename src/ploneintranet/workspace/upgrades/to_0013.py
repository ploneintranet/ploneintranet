# coding=utf-8
from plone.app.upgrade.utils import loadMigrationProfile


def subscribe_bulk_action_configurable(context):
    ''' There is a new registry record called
    ploneintranet.workspace.allow_bulk_subscribe
    that makes bulk actions configurable
    '''
    loadMigrationProfile(
        context,
        'profile-ploneintranet.workspace.upgrades:to_0013'
    )
