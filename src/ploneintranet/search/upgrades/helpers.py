# coding=utf-8
from plone import api

import logging


default_profile = 'profile-ploneintranet.search:default'
logger = logging.getLogger(__file__)


def update_registry(context):
    logger.info('Import Registry for %s', default_profile)
    context.runImportStepFromProfile(
        default_profile,
        'plone.app.registry',
        run_dependencies=False,
    )


def update_registry_filter_fields(context, new_fields, obsolete_fields=[]):
    '''
    '''
    key = 'ploneintranet.search.filter_fields'
    record = api.portal.get_registry_record(key)
    obsolete_fields = [
        field for field in obsolete_fields
        if field in record
    ]
    missing_fields = [
        field for field in new_fields
        if field not in record
    ]
    if not missing_fields and not obsolete_fields:
        logger.info('All records up to date')
        return
    if missing_fields:
        logger.info(
            'Adding records %r to the registry record %s',
            missing_fields,
            key
        )
    if obsolete_fields:
        logger.info(
            'Removing records %r to the registry record %s',
            obsolete_fields,
            key
        )
        record = tuple(
            field for field in record if field not in obsolete_fields
        )
    api.portal.set_registry_record(key, record + tuple(missing_fields))
