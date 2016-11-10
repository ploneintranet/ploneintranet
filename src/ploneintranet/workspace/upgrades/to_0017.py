# coding=utf-8
from plone.app.upgrade.utils import loadMigrationProfile


def autosave_portal_types(context):
    ''' There is a new registry record called
    ploneintranet.workspace.autosave_portal_types
    that allows to enable autosave for the selected documents
    '''
    loadMigrationProfile(
        context,
        'profile-ploneintranet.workspace.upgrades:to_0017'
    )
