# -*- coding: utf-8 -*-
from plone.app.upgrade.utils import loadMigrationProfile


def add_registry_record(context):
    """ Add registry entry for fullcalendar day span
    """
    loadMigrationProfile(
        context,
        'profile-ploneintranet.calendar.upgrades:to0003'
    )
