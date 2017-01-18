# -*- coding: utf-8 -*-
from plone.app.upgrade.utils import loadMigrationProfile


def add_splash_page_configuration(context):
    """ Add registry entries to configure splash page
    """
    loadMigrationProfile(
        context,
        'profile-ploneintranet.layout.upgrades:to_0013'
    )
