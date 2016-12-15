# -*- coding: utf-8 -*-
from plone.app.upgrade.utils import loadMigrationProfile


def add_news_portlet_configuration(context):
    """ Add registry entries to configure portlet search
    """
    loadMigrationProfile(
        context,
        'profile-ploneintranet.layout.upgrades:to_0012'
    )
