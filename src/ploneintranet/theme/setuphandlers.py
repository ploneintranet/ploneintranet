# -*- coding: utf-8 -*-
import logging
log = logging.getLogger(__name__)


def isNotPolicy(context):
    return context.readDataFile("ploneintranet.theme.txt") is None


def configureFrontPage(context):
    """ Delete the "Welcome to Plone" page and
        set the dashboard as default view
    """
    if isNotPolicy(context):
        return
    site = context.getSite()
    if "front-page" in site.objectIds():
        site.manage_delObjects(['front-page'])

    if site.hasProperty('default_page'):
        site.manage_delProperties(ids=['default_page'])
    if not site.hasProperty('layout'):
        site.manage_addProperty(id='layout',
                                value='dashboard.html',
                                type='string')
