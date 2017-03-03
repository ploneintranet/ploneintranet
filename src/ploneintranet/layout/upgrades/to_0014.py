# -*- coding: utf-8 -*-
from plone.app.upgrade.utils import loadMigrationProfile


def add_custom_dashboard_tiles(context):
    ''' Add registry entry for the custom dashboard
    '''
    loadMigrationProfile(
        context,
        'profile-ploneintranet.layout.upgrades:to_0014'
    )
