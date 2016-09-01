# coding=utf-8
import logging
from plone import api

default_profile = 'profile-ploneintranet.search:default'
logger = logging.getLogger(__file__)


def update_registry(context):
    logger.info('Import Registry for %s', default_profile)
    context.runImportStepFromProfile(
        default_profile,
        'plone.app.registry',
        run_dependencies=False,
    )


def update_registry_filter_fields(context, new_fields):
    '''
    '''
    key = 'ploneintranet.search.filter_fields'
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
