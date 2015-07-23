import logging

default_profile = 'profile-ploneintranet.workspace:default'
logger = logging.getLogger(__file__)


def import_portal_types(context):
    logger.info('Import Types Tool')
    context.runImportStepFromProfile(default_profile, 'typeinfo')
