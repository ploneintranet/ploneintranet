# -*- coding: utf-8 -*-
from plone.app.upgrade.utils import loadMigrationProfile


def add_portlet_configuration(context):
    """ Add registry entries to configure portlet expand
    """
    loadMigrationProfile(
        context,
        'profile-ploneintranet.layout.upgrades:to_0010'
    )
