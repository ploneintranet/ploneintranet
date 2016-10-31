# coding=utf-8
from ploneintranet.search.upgrades.helpers import update_registry_filter_fields


def update_registry_filter_fields_0006(context):
    new_fields = (
        u'invitees',
        u'end__gt',
        u'object_provides',
    )
    update_registry_filter_fields(context, new_fields)
