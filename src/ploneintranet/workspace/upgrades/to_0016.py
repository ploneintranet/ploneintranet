# coding=utf-8
from plone.app.upgrade.utils import loadMigrationProfile


def workspaces_sort_options(context):
    ''' There is a new registry record called
    ploneintranet.workspace.sort_options
    that allows to control in which way we sort workspaces
    '''
    loadMigrationProfile(
        context,
        'profile-ploneintranet.workspace.upgrades:to_0016'
    )
