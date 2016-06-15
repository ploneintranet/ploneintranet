from plone import api

import logging

default_profile = 'profile-ploneintranet.workspace:default'
logger = logging.getLogger(__file__)


def import_portal_types(context):
    logger.info('Import Types Tool')
    context.runImportStepFromProfile(default_profile, 'typeinfo')


def reset_empty_tags(context):
    logger.info('Resetting empty tags')
    pc = api.portal.get_tool('portal_catalog')
    empties = pc.searchResults({'Subject': ''})
    for empty in empties:
        obj = empty.getObject()
        obj.subject = ()
        obj.reindexObject()
        logger.info('Reset tags for {}'.format(obj.absolute_url()))


def import_portal_registry(context):
    logger.info('Import Registry')
    context.runImportStepFromProfile(
        default_profile,
        'plone.app.registry',
        run_dependencies=False,
    )


def import_search_registry(context):
    logger.info('Import Registry')
    context.runImportStepFromProfile(
        'profile-ploneintranet.search:default',
        'plone.app.registry',
        run_dependencies=False,
    )


def statusupdate_edit_delete(context):
    logger.info('Statusupdate edit/delete permissions')
    context.runImportStepFromProfile(default_profile, 'workflow')
    wf_tool = api.portal.get_tool('portal_workflow')
    wf_tool.updateRoleMappings()
