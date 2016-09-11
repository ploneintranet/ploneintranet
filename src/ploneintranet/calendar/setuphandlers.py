# coding=utf-8
from logging import getLogger
from plone import api

logger = getLogger()


def create_calendar_app():
    ''' Create the bookmark application
    '''
    portal = api.portal.get()
    apps = portal.apps
    if 'calendar' in apps and not apps.calendar.app:
        api.content.delete(obj=apps.calendar)
    if 'calendar' not in apps:
        api.content.create(
            container=apps,
            type='ploneintranet.layout.app',
            title=u'Calendar',
            id='calendar',
            safe_id=False,
            app='@@app-calendar',
            devices='desktop tablet'
        )

    app = apps.calendar
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
    create_calendar_app()
