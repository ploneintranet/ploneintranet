# coding=utf-8
from plone import api
import logging

default_profile = 'profile-ploneintranet.search:default'
logger = logging.getLogger(__file__)


def update_registry_filter_fields(context):
    '''
    '''
    key = 'ploneintranet.search.filter_fields'
    new_fields = (
        u'UID',
    )
    record = api.portal.get_registry_record(key)
    missing_fields = [
        field for field in new_fields
        if field not in record
    ]
    if not missing_fields:
        logger.info('All records up to date')
        return
    logger.info(
        'Adding records %r to the registry record %s',
        missing_fields,
        key
    )
    api.portal.set_registry_record(key, record + tuple(missing_fields))
