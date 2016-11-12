# coding=utf-8
from ploneintranet.search.upgrades.helpers import update_registry_filter_fields


def add_outdated_filter_field(context):
    new_fields = (
        u'outdated',
    )
    update_registry_filter_fields(context, new_fields)
