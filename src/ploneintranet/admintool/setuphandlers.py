# coding=utf-8
from logging import getLogger
from plone import api


logger = getLogger()


def create_app():
    ''' Create the administrator tool application
    '''
    portal = api.portal.get()
    apps = portal.apps
    if 'administrator-tool' not in apps:
        api.content.create(
            container=apps,
            type='ploneintranet.layout.app',
            title=u'Administrator Tool',
            id='administrator-tool',
            safe_id=False,
            app='@@app-administrator-tool',
            devices='desktop tablet'
        )

    app = apps['administrator-tool']
    if api.content.get_state(app) == 'published':
        return
    try:
        api.content.transition(app, to_state='published')
    except:
        logger.exception('Cannot publish the app: %r', app)


def post_default(context):
    ''' Actions needed after importing
    the ploneintranet.admintool:default profile
    '''
    create_app()
