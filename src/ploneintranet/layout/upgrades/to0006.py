# -*- coding: utf-8 -*-
from plone.app.upgrade.utils import loadMigrationProfile


def setup_login_splash(context):
    """ Load the new registry record for the login splash
    """
    loadMigrationProfile(
        context,
        'profile-ploneintranet.layout.upgrades:to_0006'
    )
