# coding=utf-8
from ploneintranet.search.upgrades.helpers import update_registry_filter_fields


def update_registry_filter_fields_0003(context):
    '''
    '''
    new_fields = (
        u'Creator',
    )
    update_registry_filter_fields(context, new_fields)
