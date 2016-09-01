from plone import api

import logging

logger = logging.getLogger(__file__)

default_profile = 'profile-ploneintranet.workspace:default'


def bulk_actions_configuration(context):
    # Add the 'outdated' index for archiving
    context.runImportStepFromProfile(
        default_profile,
        'catalog',
        run_dependencies=False,
    )
    # No idea why this isn't installed and configured as a dependency
    qi = api.portal.get_tool('portal_quickinstaller')
    qi.installProduct('Products.CMFNotification')
    context.runImportStepFromProfile(
        default_profile,
        'cmfnotification',
        run_dependencies=False,
    )
