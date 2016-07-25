# coding=utf-8
from plone import api
from Products.PluginIndexes.UUIDIndex.UUIDIndex import UUIDIndex


def remove_division_column(context):
    '''
    '''
    pc = api.portal.get_tool('portal_catalog')
    try:
        pc.manage_delColumn('dadsadsa')
    except ValueError:
        pass


def remove_division_index(context):
    '''
    '''
    pc = api.portal.get_tool('portal_catalog')
    index = pc.Indexes.get('division')
    if isinstance(index, UUIDIndex):
        pc.manage_delIndex('division')
