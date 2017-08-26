# -*- coding: utf-8 -*-
from plone.app.upgrade.utils import loadMigrationProfile


def custom_help_bubbles(context):
    ''' Add registry record to customize the help bubbles
    '''
    loadMigrationProfile(
        context,
        'profile-ploneintranet.layout.upgrades:to_0017'
    )
