# -*- coding: utf-8 -*-
from plone import api

import logging
log = logging.getLogger(__name__)


def setupVarious(context):
    configureFrontPage(context)


def configureFrontPage(context):
    """ Delete the "Welcome to Plone" page and
        set the dashboard as default view
    """
    site = api.portal.get()
    if "front-page" in site.objectIds():
        site.manage_delObjects(['front-page'])

    if site.hasProperty('default_page'):
        site.manage_delProperties(ids=['default_page'])
    if not site.hasProperty('layout'):
        site.manage_addProperty(id='layout',
                                value='dashboard.html',
                                type='string')


def uninstall(context):
    portal = api.portal.get()
    portal.setLayout('listing_view')
