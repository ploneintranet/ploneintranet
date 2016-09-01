# coding=utf-8
from logging import getLogger
from plone import api

logger = getLogger()


def create_bookmark_app():
    ''' Create the bookmark application
    '''
    portal = api.portal.get()
    apps = portal.apps
    if 'bookmarks' not in apps:
        api.content.create(
            container=apps,
            type='ploneintranet.layout.app',
            title=u'Bookmarks',
            id='bookmarks',
            safe_id=False,
            app='@@app-bookmarks',
            devices='desktop tablet mobile'
        )

    app = apps.bookmarks
    if api.content.get_state(app) == 'published':
        return
    try:
        api.content.transition(app, to_state='published')
    except:
        logger.exception('Cannot publish the app: %r', app)


def post_default(context):
    ''' Actions needed after importing
    the ploneintranet.bookmarks:default profile
    '''
    create_bookmark_app()
