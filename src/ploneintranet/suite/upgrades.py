# coding=utf-8
from plone import api
from ploneintranet.themeswitcher.interfaces import IThemeSwitcherSettings
from Products.CMFPlone.utils import safe_unicode

import logging


default_profile = 'profile-ploneintranet.suite:default'
logger = logging.getLogger(__file__)


def import_portal_registry(context):
    logger.info('Import Registry')
    context.runImportStepFromProfile(
        'profile-ploneintranet.docconv.client:default',
        'plone.app.registry',
        run_dependencies=False,
    )


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


def filter_news_layer(context):
    ''' Filter the news layer when the PI theme is switched off
    '''
    try:
        filter_list = api.portal.get_registry_record(
            interface=IThemeSwitcherSettings,
            name='browserlayer_filterlist',
        )
    except api.exc.InvalidParameterError:
        # record not there => nothing to update
        return

    new_ifaces = [
        iface for iface in (
            'ploneintranet.news.browser.interfaces.INewsLayer',
            'ploneintranet.news.browser.interfaces.INewsContentLayer',
        )
        if iface not in filter_list
    ]
    if not new_ifaces:
        # no ifaces to add => nothing to update
        return

    filter_list.extend(new_ifaces)
    filter_list = [safe_unicode(iface) for iface in filter_list]
    api.portal.set_registry_record(
        interface=IThemeSwitcherSettings,
        name='browserlayer_filterlist',
        value=filter_list,
    )


def to_0016(context):
    ''' Since this version we have ploneintranet.admintool
    '''
    pq = api.portal.get_tool('portal_quickinstaller')
    if not pq.isProductInstalled('ploneintranet.admintool'):
        pq.installProduct('ploneintranet.admintool')
