# coding=utf-8
from plone.app.upgrade.utils import loadMigrationProfile


def update_rolemap(context):
    ''' We have a new permission "Plone Intranet: Use Messaging" that needs
        to be granted to the correct roles
    '''
    loadMigrationProfile(
        context,
        'profile-ploneintranet.messaging.upgrades:to_0002'
    )
