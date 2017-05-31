# coding=utf-8
from ploneintranet.search.upgrades.helpers import update_registry_filter_fields


def add_todo_app_solr_fields(context):
    new_fields = (
        u'assignee',
        u'due__ge',
        u'due__le',
        u'due__range',
        u'initiator',
    )
    update_registry_filter_fields(context, new_fields)
