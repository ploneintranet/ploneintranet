# -*- coding: utf-8 -*-
from plone.app.upgrade.utils import loadMigrationProfile


def add_query_boost_configuration(context):
    """ Add registry entry for solr function query boost
    """
    loadMigrationProfile(
        context,
        'profile-ploneintranet.search.upgrades:to_0009'
    )
