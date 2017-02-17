# -*- coding: utf-8 -*-
from plone.app.upgrade.utils import loadMigrationProfile


def add_field_limit_configuration(context):
    """ Add registry entry for solr field limit
    """
    loadMigrationProfile(
        context,
        'profile-ploneintranet.search.upgrades:to_0010'
    )
