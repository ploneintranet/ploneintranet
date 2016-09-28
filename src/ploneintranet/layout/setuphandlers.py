# -*- coding: utf-8 -*-
from plone import api
from ploneintranet.layout.app import apps_container_id

import logging
log = logging.getLogger(__name__)


def setupVarious(context):
    configureFrontPage(context)
    create_apps_container()
    sort_portal_tabs()


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


def create_apps(*args):
    ''' Create the known ploneintranet apps
    '''
    portal = api.portal.get()
    app_container = portal.get(apps_container_id)

    # Actual content-containing apps, like 'news' and 'library'
    # are created by their own package.
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
            'key': 'case-manager',
            'title': u'Case manager',
            'path': '@@case-manager',
            'devices': 'desktop tablet'
        }, {
            'key': 'app-market',
            'title': u'App market',
        }
    ]
    for app_spec in apps:
        # if the app is not there we will create it
        if app_spec['key'] not in app_container:
            api.content.create(
                container=app_container,
                type='ploneintranet.layout.app',
                title=app_spec['title'],
                id=app_spec['key'],
                safe_id=False,
                app=app_spec.get('path', u''),
                devices=app_spec.get('devices', 'desktop'),
            )
        # update the app object
        app_obj = app_container[app_spec['key']]
        for attr in ('title', 'app', 'devices'):
            if attr == 'app':
                attr_spec = app_spec.get('path')
            else:
                attr_spec = app_spec.get(attr)
            if getattr(app_obj, attr) != attr_spec:
                setattr(app_obj, attr, attr_spec)
        # if the app is not published we will publish it
        if api.content.get_state(app_obj) != 'published':
            try:
                api.content.transition(app_obj, to_state='published')
            except:
                log.exception('Cannot publish the app: %r', app_obj)


def sort_portal_tabs(*args):
    portal_tabs = api.portal.get_tool('portal_actions').portal_tabs
    current = portal_tabs.objectIds()
    goal = [x for x in ('index_html',
                        'dashboard',
                        'news',
                        'library',
                        'workspaces',
                        'apps')
            if x in current]
    for id in goal:
        if portal_tabs.getObjectPosition(id) != goal.index(id):
            portal_tabs.moveObjectToPosition(id, goal.index(id))


def uninstall(context):
    portal = api.portal.get()
    portal.setLayout('listing_view')
