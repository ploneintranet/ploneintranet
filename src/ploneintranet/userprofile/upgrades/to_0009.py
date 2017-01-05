# coding=utf-8
from plone.app.upgrade.utils import loadMigrationProfile


def portlet_contacts_byline_field_registry_record(context):
    ''' There is a new registry record called
    ploneintranet.userprofile.portlet_contacts_byline_field
    '''
    loadMigrationProfile(
        context,
        'profile-ploneintranet.userprofile.upgrades:to_0009',
    )
