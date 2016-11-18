# -*- coding: utf-8 -*-
from plone import api
from plone.app.textfield.value import RichTextValue
from plone.namedfile.file import NamedBlobImage
from ploneintranet.news.content import INewsApp
from z3c.relationfield.relation import create_relation

import logging
import loremipsum
import os
log = logging.getLogger(__name__)


def setupVarious(context):
    app = create_news_app()
    move_all_newsitems_to_app(app)


def create_news_app():
    portal = api.portal.get()
    if 'news' in portal:
        app_obj = portal.news
        if not INewsApp.providedBy(app_obj):
            api.content.delete(obj=app_obj, check_linkintegrity=False)
    if 'news' not in portal:
        api.content.create(
            container=portal,
            type='ploneintranet.news.app',
            title='News publisher',
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
        title=LOREMIPSUM_TITLES[i],
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


LOREMIPSUM_TITLES = [u'Etiam augue.', u'Fames vitae.', u'Dolor etiam mauris lobortis nibh torquent dis natoque torquent cubilia.', u'Class lacus semper erat laoreet et accumsan gravida aliquet mauris luctus mi eros.', u'Vitae ipsum metus nonummy tempus lorem netus vivamus dui ad cursus leo orci inceptos eni fames.', u'Proin netus.', u'Felis proin senectus quis non est.', u'Massa lacus sociis molestie odio pretium.', u'Class velit dis velit integer.', u'Fusce fames.', u'Felis fusce nec duis ac non vitae donec magnis cursus molestie.', u'Magna nulla vitae purus lacus tempus.', u'Etiam purus aptent lacus adipiscing sociosqu commodo sapien id euismod amet lorem in lorem.', u'Magna felis congue maecenas dolor tincidunt quis ipsum taciti suspendisse lacus hymenaeos.', u'Dolor vitae metus habitant class dignissim pede per leo nam viverra ante non ipsum vestibulum.', u'Netus fames sociosqu.', u'Fusce morbi sit nisl velit commodo eleifend nonummy elit ut consectetuer.', u'Etiam vitae sapien suspendisse curae aptent imperdiet.', u'Neque nulla fusce luctus magna mattis ligula vel amet fames.', u'Purus augue suspendisse at mauris mus dis et posuere.']  # noqa
