# -*- coding: utf-8 -*-
from plone import api
from plone.app.textfield.value import RichTextValue
from plone.namedfile.file import NamedBlobImage
from z3c.relationfield.relation import create_relation

import loremipsum
import logging
import os
log = logging.getLogger(__name__)


def setupVarious(context):
    app = create_news_app()
    move_all_newsitems_to_app(app)


def create_news_app():
    portal = api.portal.get()
    if 'news' not in portal:
        api.content.create(
            container=portal,
            type='ploneintranet.news.app',
            title='News',
            id='news',
            safe_id=False,
        )
    app_obj = portal.news
    app_obj.indexObject()
    # if the app is not published we will publish it
    if api.content.get_state(app_obj) != 'published':
        try:
            api.content.transition(app_obj, to_state='published')
        except:
            log.exception('Cannot publish the app: %r', app_obj)
    # there always must be 1 or more news sections
    if not app_obj.objectValues():
        section = api.content.create(
            container=app_obj,
            type='ploneintranet.news.section',
            title='Company News',
            id='company-news',
            safe_id=False,
        )
        section.indexObject()
    return app_obj


def move_all_newsitems_to_app(app):
    section = app.sections()[0]
    app_path = '/'.join(app.getPhysicalPath())
    catalog = api.portal.get_tool('portal_catalog')
    items = [x for x in catalog(portal_type='News Item')
             if not x.getPath().startswith(app_path)]
    for item in items:
        moved = api.content.move(item.getObject(), app)
        moved.section = create_relation(section.getPhysicalPath())
        moved.reindexObject()


def setupTestdata(context):
    context = context._getImportContext('profile-ploneintranet.news:testing')
    portal = api.portal.get()
    if 'news' in portal.objectIds():
        api.content.delete(portal.news)
    news = create_news_app()
    company_news = news['company-news']
    press_mentions = api.content.create(
        container=news,
        type='ploneintranet.news.section',
        title='Press Mentions',
        id='press-mentions',
        safe_id=False,
    )
    api.content.transition(company_news, 'publish')
    company_news.reindexObject()
    api.content.transition(press_mentions, 'publish')
    press_mentions.reindexObject()
    for i in range(5):
        create_news_items(context, news, company_news, i)
    for i in range(5, 10):
        create_news_items(context, news, press_mentions, i)


def create_news_items(context, app, section, i):
    seq = i + 1
    item = api.content.create(
        container=app,
        type='News Item',
        title=loremipsum.get_sentence(),
    )
    item.section = create_relation(section.getPhysicalPath())
    item.description = ' '.join(loremipsum.get_sentences(2))
    item.text = RichTextValue(raw="\n\n".join(loremipsum.get_paragraphs(3)),
                              mimeType='text/plain',
                              outputMimeType='text/x-html-safe')
    img_name = '{:02d}.jpg'.format(seq)
    img_path = os.path.join('images', img_name)
    img_data = context.openDataFile(img_path).read()
    item.image = NamedBlobImage(data=img_data,
                                filename=img_name.decode('utf-8'))
    item.setEffectiveDate('2016/09/{:02d}'.format(seq))
    api.content.transition(item, 'publish')
    item.reindexObject()
