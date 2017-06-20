# coding=utf-8
from logging import getLogger
from plone import api
from ploneintranet.todo.interfaces import ITodoApp
from zope.interface import alsoProvides


logger = getLogger()


def create_app():
    ''' Create the task application
    '''
    portal = api.portal.get()
    apps = portal.apps
    if 'todo' not in apps:
        api.content.create(
            container=apps,
            type='ploneintranet.layout.app',
            title=u'Todo',
            id='todo',
            safe_id=False,
            app='@@app-todo',
            devices='desktop tablet mobile'
        )
        alsoProvides(apps['todo'], ITodoApp)

    app = apps['todo']
    if api.content.get_state(app) == 'published':
        return
    try:
        api.content.transition(app, to_state='published')
    except:
        logger.exception('Cannot publish the app: %r', app)


def post_default(context):
    ''' Actions needed after importing
    the ploneintranet.todo:default profile
    '''
    create_app()
