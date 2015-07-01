# -*- coding: utf-8 -*-
from plone import api

import logging
log = logging.getLogger(__name__)


def setupVarious(context):
    if context.readDataFile("ploneintranet.layout_default.txt") is None:
        return

    configureFrontPage(context)


def configureFrontPage(context):
    """ Delete the "Welcome to Plone" page and
        set the dashboard as default view
    """
    site = context.getSite()
    if "front-page" in site.objectIds():
        site.manage_delObjects(['front-page'])

    if site.hasProperty('default_page'):
        site.manage_delProperties(ids=['default_page'])
    if not site.hasProperty('layout'):
        site.manage_addProperty(id='layout',
                                value='dashboard.html',
                                type='string')


def uninstall(context):
    if context.readDataFile('ploneintranet.layout_uninstall.txt') is None:
        return
    portal = api.portal.get()
    portal.setLayout('listing_view')
