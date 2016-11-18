# coding=utf-8
from plone import api
from plone.registry.field import TextLine
from plone.registry.record import Record


def setup_default_grouping(context):
    ''' Add a registry record if it is not there
    '''
    pr = api.portal.get_tool('portal_registry')
    key = 'ploneintranet.workspace.default_grouping'
    if key in pr.records:
        return
    pr.records[key] = Record(TextLine(), u'folder')
