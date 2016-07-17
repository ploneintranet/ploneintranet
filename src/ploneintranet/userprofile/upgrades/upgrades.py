# coding=utf-8
import logging

default_profile = 'profile-ploneintranet.userprofile:default'
logger = logging.getLogger(__file__)


def import_portal_registry(context):
    logger.info('Import Registry')
    context.runImportStepFromProfile(
        default_profile,
        'plone.app.registry',
        run_dependencies=False,
    )
