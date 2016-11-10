# coding=utf-8
from .base import import_catalog


def activate_invitees(context):
    import_catalog(context, indexes=['invitees'])
