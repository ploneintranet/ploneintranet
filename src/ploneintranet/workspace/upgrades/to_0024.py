# coding=utf-8
from plone.app.upgrade.utils import loadMigrationProfile


def create_preserve_template_ownership_record(context):
    ''' There is a new registry record called
    ploneintranet.workspace.preserve_template_ownership
    that keeps the ownership of a ws template after it is copied
    '''
    loadMigrationProfile(
        context,
        'profile-ploneintranet.workspace.upgrades:to_0024'
    )
