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
