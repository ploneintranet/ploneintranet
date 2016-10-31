# coding=utf-8
from plone.app.upgrade.utils import loadMigrationProfile


def add_mail_type(context):
    ''' There is a new ``ploneintranet.workspace.mail`` portal type
    since version 0011.
    We have a profile to include it in ploneintranet.
    '''
    loadMigrationProfile(
        context,
        'profile-ploneintranet.workspace.upgrades:to_0011'
    )
