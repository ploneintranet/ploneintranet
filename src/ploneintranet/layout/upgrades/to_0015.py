# -*- coding: utf-8 -*-
from plone.app.upgrade.utils import loadMigrationProfile


def add_known_bad_ips(context):
    ''' Add registry entry for known bad ipds
    '''
    loadMigrationProfile(
        context,
        'profile-ploneintranet.layout.upgrades:to_0015'
    )
