# -*- coding: utf-8 -*-
from plone.app.upgrade.utils import loadMigrationProfile
from ploneintranet.layout.setuphandlers import create_apps_container


def add_apps_container(context):
    """
        Load the new types information for the Apps container
    """
    loadMigrationProfile(
        context,
        'profile-ploneintranet.layout.upgrades:to_0004'
    )
    # Create the apps container
    create_apps_container()
