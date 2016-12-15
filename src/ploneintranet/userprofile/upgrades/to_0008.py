# coding=utf-8
from plone.app.upgrade.utils import loadMigrationProfile


def portlet_contacts_recent_registry_record(context):
    ''' There is a new registry record called
    ploneintranet.userprofile.portlet_contacts_recent
    '''
    loadMigrationProfile(
        context,
        'profile-ploneintranet.userprofile.upgrades:to_0008',
    )
