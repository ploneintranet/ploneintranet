# coding=utf-8
from plone.app.upgrade.utils import loadMigrationProfile


def create_autorename_record(context):
    ''' There is a new registry record called
    ploneintranet.workspace.rename_after_title_changed
    that toggles the event that automatically
    renames the objects if the title changes
    '''
    loadMigrationProfile(
        context,
        'profile-ploneintranet.workspace.upgrades:to_0023'
    )
