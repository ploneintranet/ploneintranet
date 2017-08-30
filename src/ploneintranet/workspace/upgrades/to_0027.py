# coding=utf-8
from plone.app.upgrade.utils import loadMigrationProfile


def configure_autosave_delay(context):
    ''' There is a new registry record called
    ploneintranet.workspace.autosave_delay
    '''
    loadMigrationProfile(
        context,
        'profile-ploneintranet.workspace.upgrades:to_0027'
    )
