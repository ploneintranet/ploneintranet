# -*- coding: utf-8 -*-
from plone.app.upgrade.utils import loadMigrationProfile


def toggle_help_bubbles(context):
    ''' Add registry record to toggle on and off the help bubbles
    '''
    loadMigrationProfile(
        context,
        'profile-ploneintranet.layout.upgrades:to_0018'
    )
