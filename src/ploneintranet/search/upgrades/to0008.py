# coding=utf-8
from plone import api
from plone.registry.field import Bool
from plone.registry.record import Record


def add_solr_disabled_field(context):
    ''' Add a registry record if it is not there
    '''
    pr = api.portal.get_tool('portal_registry')
    key = 'ploneintranet.search.solr.disabled'
    if key in pr.records:
        return
    pr.records[key] = Record(Bool(), False)
