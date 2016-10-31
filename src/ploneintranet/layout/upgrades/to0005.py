# -*- coding: utf-8 -*-
from plone.app.upgrade.utils import loadMigrationProfile
from ploneintranet.layout.setuphandlers import create_apps


def add_apps(context):
    """
        Load the new types information for the Apps container
    """
    loadMigrationProfile(
        context,
        'profile-ploneintranet.layout.upgrades:to_0005'
    )
    create_apps()
