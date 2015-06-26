from plone import api
import logging

log = logging.getLogger(__name__)


def setupVarious(context):
    if context.readDataFile('ploneintranet.library_default.txt') is None:
        return

    log.info('setupVarious')
    portal = context.getSite()
    catalog = api.portal.get_tool('portal_catalog')
    if len(catalog(portal_type='ploneintranet.library.app')) == 0:
        library = api.content.create(
            type='ploneintranet.library.app',
            title='Library',
            container=portal)
        api.content.transition(library, "publish")
