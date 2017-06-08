# -*- coding: utf-8 -*-
from plone.app.upgrade.utils import loadMigrationProfile


def add_library_configuration(context):
    """ Add registry entries to configure splash page
    """
    loadMigrationProfile(
        context,
        'profile-ploneintranet.library.upgrades:to_0004'
    )
