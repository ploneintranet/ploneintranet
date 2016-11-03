# coding=utf-8
from .base import import_catalog


def activate_timezone(context):
    import_catalog(context, indexes=['timezone'])
