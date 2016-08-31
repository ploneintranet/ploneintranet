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


def create_apps_container(with_apps=True):
    portal = api.portal.get()

    if apps_container_id not in portal:
        apps_container = api.content.create(
            container=portal,
            type='ploneintranet.layout.appscontainer',
            title='Apps'
        )
        api.content.transition(apps_container, 'publish')

    if with_apps:
        create_apps()


def create_apps():
    ''' Create the known ploneintranet apps
    '''
    portal = api.portal.get()
    app_container = portal.apps

    # BBB: Find me a better place
    apps = [
        {
            'key': 'contacts',
            'title': u'Contacts',
            'devices': 'desktop tablet'
        }, {
            'key': 'messages',
            'title': u'Messages',
            'path': '@@app-messaging',
        }, {
            'key': 'todo',
            'title': u'Todo',
        }, {
            'key': 'calendar',
            'title': u'Calendar',
        }, {
            'key': 'slide-bank',
            'title': u'Slide bank',

        }, {
            'key': 'image-bank',
            'title': u'Image bank',
        }, {
            'key': 'news',
            'title': u'News publisher',
        }, {
            'key': 'case-manager',
            'title': u'Case manager',
            'path': '@@case-manager',
            'devices': 'desktop tablet'
        }, {
            'key': 'app-market',
            'title': u'App market',
        }
    ]
    for app in apps:
        # if the app is not there we will create it
        if app['key'] not in app_container:
            api.content.create(
                container=app_container,
                type='ploneintranet.layout.app',
                title=app['title'],
                id=app['key'],
                safe_id=False,
                app=app.get('path', u''),
                devices=app.get('devices', 'desktop'),
            )
        # if the app is published we will publish it
        app = app_container[app['key']]
        if api.content.get_state(app) != 'published':
            try:
                api.content.transition(app, to_state='published')
            except:
                log.exception('Cannot publish the app: %r', app)


def uninstall(context):
    portal = api.portal.get()
    portal.setLayout('listing_view')
