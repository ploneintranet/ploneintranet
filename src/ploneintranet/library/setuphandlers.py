# coding=utf-8
from plone import api
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import INavigationSchema
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

import logging

log = logging.getLogger(__name__)


def setupVarious(context):
    log.info('setupVarious')
    portal = api.portal.get()
    catalog = api.portal.get_tool('portal_catalog')
    if len(catalog(portal_type='ploneintranet.library.app')) == 0:
        api.content.create(
            type='ploneintranet.library.app',
            title='Library',
            container=portal)

    # profiles/default/registry.xml has no effect
    registry = getUtility(IRegistry)
    nav_settings = registry.forInterface(INavigationSchema, prefix="plone")
    plone_utils = api.portal.get_tool('plone_utils')

    # this is the constraint for the registry record "displayed_types"
    constraint = getUtility(
        IVocabularyFactory,
        'plone.app.vocabularies.ReallyUserFriendlyTypes'
    )
    allowed_types = {item.value for item in constraint(context)}
    nav_settings.displayed_types = tuple(
        t for t in plone_utils.getUserFriendlyTypes() if t in allowed_types
    )
