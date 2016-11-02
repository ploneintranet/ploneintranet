# -*- coding: utf-8 -*-
from chameleon import PageTemplateLoader
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from ploneintranet.layout.utils import shorten
from plone.memoize.view import memoize

from ploneintranet.core import ploneintranetCoreMessageFactory as _

import logging
import os

log = logging.getLogger(__name__)
path = os.path.dirname(__file__)


class NewsMagazine(BrowserView):

    section_id = None

    templates = PageTemplateLoader(os.path.join(path, "templates"))

    @property
    @memoize
    def app(self):
        return self.context

    def sections(self):
        # TODO: add 'trending'
        app_current = self.section_id is None
        sections = [dict(title=_('All news'),
                         absolute_url=self.app.absolute_url(),
                         css_class=app_current and 'current' or '')]
        for section in self.app.sections(list_items=False):
            current = self.section_id == section['id']
            section['css_class'] = current and 'current' or ''
            sections.append(section)
        return sections

    @memoize
    def news_items(self):
        return self.app.news_items(section_id=self.section_id,
                                   desc_len=120)

    @memoize
    def trending_items(self):
        all_trending = self.context.news_items('trending', desc_len=120)
        return [x for x in all_trending if x not in self.news_items()[0:4]]

    def trending_top5(self):
        return self.trending_items()[0:5]

    def trending_hasmore(self):
        return bool(self.trending_items()[5:6])


class FeedItem(BrowserView):

    def can_edit(self):
        return api.user.has_permission('Modify',
                                       obj=self.context)

    def description(self, desc_len=160):
        return shorten(self.context.description, desc_len)

    def date(self):
        return self.context.effective().strftime('%B %d, %Y')

    def category(self):
        return self.context.section.to_object.title


class NewsSectionView(NewsMagazine):

    @property
    @memoize
    def section_id(self):
        return self.context.id

    @property
    @memoize
    def app(self):
        return self.context.aq_parent


class NewsPublisher(BrowserView):

    sidebar = ViewPageTemplateFile('templates/publisher-sidebar.pt')

    @property
    def app_url(self):
        return '{}/publisher'.format(self.context.absolute_url())

    def __call__(self):
        if self.request.method == 'POST':
            self.update()
        return super(NewsPublisher, self).__call__()

    def update(self):
        get = self.request.form.get
        if get('form.id') == 'create':
            if get('type') == 'section':
                self.create_section()
            elif get('type') == 'item':
                self.create_item()

    def create_section(self):
        get = self.request.form.get
        title = get('section_title', '')
        if not title:
            log.error("No title given for section creation")
            return
        description = get('section_description', '')
        section_visible = bool(get('section-visible', False))
        description_visible = bool(get('section-description-visible', False))
        section = api.content.create(
            container=self.context,
            type='ploneintranet.news.section',
            title=title,
            description=description,
            section_visible=section_visible,
            description_visible=description_visible
        )
        log.info("Created section {}".format(section))

    def create_item(self):
        get = self.request.form.get
        title = get('item_title', '')
        if not title:
            log.error("No title given for item creation")
            return
        description = get('item_description', '')
        visibility = bool(get('item_visibility', False))
        item = api.content.create(
            container=self.context,
            type='News Item',
            title=title,
            description=description,
            visibility=visibility,
        )
        log.info("Created news item {}".format(item))


class SectionEdit(BrowserView):

    @property
    def url(self):
        return self.request.get('ACTUAL_URL')

    @property
    def app_url(self):
        return '{}/publisher'.format(self.context.aq_parent.absolute_url())

    def __call__(self):
        if self.request.method == 'POST':
            self.update()
            return self.request.response.redirect(self.app_url)
        else:
            return super(SectionEdit, self).__call__()

    def update(self):
        get = self.request.form.get
        title = get('title', '')
        if not title:
            log.error("No title given for section update")
            return
        self.context.title = title
        self.context.description = get('description', '')
        self.context.section_visible = bool(get('section-visible', False))
        self.context.description_visible = bool(
            get('section-description-visible', False))


class SectionDelete(SectionEdit):

    def update(self):
        log.info("Deleting {}".format(self.context))
        api.content.delete(obj=self.context, check_linkintegrity=False)
