# coding=utf-8
from plone import api
import logging

default_profile = 'profile-ploneintranet.suite:default'
logger = logging.getLogger(__file__)


def barceloneta_workspace(context):
    logger.info("Enabling barceloneta specific browser layer")
    context.runImportStepFromProfile(
        'profile-ploneintranet.workspace:default',
        'browserlayer',
        run_dependencies=False,
    )
    context.runImportStepFromProfile(
        default_profile,
        'plone.app.registry',
        run_dependencies=False,
    )


def to_0009(context):
    ''' Since this version we have ploneintranet.bookmarks
    '''
    pq = api.portal.get_tool('portal_quickinstaller')
    if not pq.isProductInstalled('ploneintranet.bookmarks'):
        pq.installProduct('ploneintranet.bookmarks')
