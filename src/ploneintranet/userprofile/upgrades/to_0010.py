# coding=utf-8
from plone.app.upgrade.utils import loadMigrationProfile


def personal_tasks(context):
    ''' Allow the creation of tasks inside a userprofile
    '''
    loadMigrationProfile(
        context,
        'profile-ploneintranet.userprofile.upgrades:to_0010',
    )
