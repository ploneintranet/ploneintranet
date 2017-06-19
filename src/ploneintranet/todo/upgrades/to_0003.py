# coding=utf-8
from datetime import datetime
from plone import api


def fix_existing_dates(context):
    portal_catalog = api.portal.get_tool('portal_catalog')
    results = portal_catalog(portal_type='todo')
    for res in results:
        todo = res.getObject()
        if isinstance(todo.due, datetime):
            todo.due = todo.due.date()
