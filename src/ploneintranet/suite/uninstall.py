# -*- coding: utf-8 -*-
from plone import api
from zExceptions import BadRequest
import logging

log = logging.getLogger(__name__)


# dependencies of our dependencies that will be removed
ADDITIONAL_DEPENDENCIES = [
    'slc.docconv',
    'collective.workspace',
    'collective.documentviewer',
]


def uninstall(context):
    if context.readDataFile('ploneintranet.suite_uninstall.txt') is None:
        return
    portal = api.portal.get()
    uninstall_dependencies(portal)


def uninstall_dependencies(portal):
    # Uninstall all dependencies of ploneintranet and its dependencies
    # We do not check if the product is installed since it may be
    # INonInstallable
    qi = api.portal.get_tool('portal_quickinstaller')
    install_profile = qi.getInstallProfile('ploneintranet.suite')
    dependencies = install_profile.get('dependencies', ())
    dependencies = list(dependencies)
    dependencies.extend(ADDITIONAL_DEPENDENCIES)
    for dependency in dependencies:
        dependency = str(dependency.split('profile-')[-1].split(':')[0])
        try:
            qi.uninstallProducts([dependency])
            log.info('Uninstalled dependency "%s"' % dependency)
        except (AttributeError, BadRequest):
            pass
