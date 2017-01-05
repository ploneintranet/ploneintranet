# coding=utf-8
from plone.app.upgrade.utils import loadMigrationProfile


def create_clicktracker_registry_record(context):
    ''' There is a new registry record called
    ploneintranet.workspace.include_slcclicktracker
    that toggles inclusion of an slcclicktracker element in the content default
    view templates
    '''
    loadMigrationProfile(
        context,
        'profile-ploneintranet.workspace.upgrades:to_0022'
    )
