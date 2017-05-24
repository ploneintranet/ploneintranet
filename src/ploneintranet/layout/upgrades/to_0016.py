# -*- coding: utf-8 -*-
from plone.app.upgrade.utils import loadMigrationProfile


def new_splashpage(context):
    ''' Add registry entry for for the new_splashpage
    '''
    loadMigrationProfile(
        context,
        'profile-ploneintranet.layout.upgrades:to_0016'
    )
