# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from ploneintranet.layout.utils import shorten
from plone.memoize.view import memoize

from ploneintranet.workspace.basecontent import baseviews
from .utils import obj2dict

import logging

log = logging.getLogger(__name__)


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

    @memoize
    def sections(self):
        _sections = []
        for section in self.context.sections():
            news_items = self.news_items(section.id)
            delete_protected = len(news_items) == 0
            _sections.append(obj2dict(
                section,
                'id', 'title', 'description', 'absolute_url',
                news_items=news_items,
                delete_protected=delete_protected
            ))
        if len(_sections) == 1:
            _sections[0]['delete_protected'] = True
        return _sections

    @memoize
    def news_items(self, section_id=None, desc_len=160):
        _items = []
        i = 0
        for item in self.context.news_items(section_id):
            i += 1
            _items.append(obj2dict(
                item,
                'id', 'title', 'absolute_url',
                description=shorten(item.description, desc_len),
                date=item.effective().strftime('%B %d, %Y'),
                category=item.section.to_object.title,
                counter=i,
                can_edit=api.user.has_permission('Modify', obj=item)
            ))
        return _items

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


class NewsItemEdit(baseviews.ContentView):

    @property
    def app(self):
        return self.context.aq_parent

    def sidebar(self):
        publisher = api.content.get_view('publisher', self.app, self.request)
        return publisher.sidebar()

    def can_review(self):
        return api.user.has_permission('Review portal content',
                                       obj=aq_inner(self.context))
