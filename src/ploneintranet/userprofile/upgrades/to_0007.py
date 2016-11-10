# coding=utf-8
from plone.app.upgrade.utils import loadMigrationProfile


def only_membrane_groups_registry_record(context):
    ''' There is a new registry record called
    ploneintranet.userprofile.only_membrane_groups
    '''
    loadMigrationProfile(
        context,
        'profile-ploneintranet.userprofile.upgrades:to_0007',
    )
