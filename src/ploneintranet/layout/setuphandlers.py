# -*- coding: utf-8 -*-
from plone import api
from ploneintranet.layout.app import apps_container_id

import logging
log = logging.getLogger(__name__)


def setupVarious(context):
    configureFrontPage(context)
    create_apps_container()


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


def create_apps_container():
    portal = api.portal.get()

    if apps_container_id not in portal:
        apps_container = api.content.create(
            container=portal,
            type='ploneintranet.layout.appscontainer',
            title='Apps'
        )
        api.content.transition(apps_container, 'publish')


def uninstall(context):
    portal = api.portal.get()
    portal.setLayout('listing_view')
