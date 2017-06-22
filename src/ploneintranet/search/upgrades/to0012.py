# coding=utf-8
from ploneintranet.search.upgrades.helpers import update_registry_filter_fields


def add_todo_app_solr_fields(context):
    new_fields = (
        u'assignee',
        u'due__gt',
        u'due__lt',
        u'due__range',
        u'initiator',
    )
    obsolete_fields = (
        u'due__ge',
        u'due__le',
    )
    update_registry_filter_fields(
        context,
        new_fields,
        obsolete_fields,
    )
