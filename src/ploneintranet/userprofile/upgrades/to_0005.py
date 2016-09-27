# coding=utf-8
from plone.app.upgrade.utils import loadMigrationProfile


def add_userprofile_hidden_info_registry_entry(context):
    ''' There is a new registry record called
    ploneintranet.userprofile.userprofile_hidden_info
    that makes the profile view configurable
    '''
    loadMigrationProfile(
        context,
        'profile-ploneintranet.userprofile.upgrades:to_0005'
    )
