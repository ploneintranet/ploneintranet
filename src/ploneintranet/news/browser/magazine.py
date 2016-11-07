# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from plone import api
from ploneintranet.layout.utils import shorten
from plone.memoize.view import memoize

from ploneintranet.core import ploneintranetCoreMessageFactory as _
from .utils import obj2dict


class NewsMagazine(BrowserView):

    section_id = ''

    @property
    @memoize
    def app(self):
        return self.context

    @memoize
    def sections(self):
        # TODO: add 'trending'
        app_current = self.section_id is None
        sections = [dict(title=_('All news'),
                         absolute_url=self.app.absolute_url(),
                         css_class=app_current and 'current' or '')]
        for section in self.app.sections():
            current = self.section_id == section.id
            css_class = current and 'current' or ''
            sections.append(obj2dict(
                section,
                'absolute_url', 'title',
                current=current, css_class=css_class
            ))
        return sections

    @memoize
    def news_items(self, section_id=''):
        if section_id != '':
            section_id = self.section_id
        items = []
        i = 0
        for item in self.app.news_items(section_id):
            if api.content.get_state(item) != 'published':
                continue
            if not item.magazine_home:
                continue
            i += 1
            items.append(obj2dict(item, counter=i))
        return items

    @memoize
    def trending_items(self):
        all_trending = self.news_items('trending')
        return [x for x in all_trending if x not in self.news_items()[0:4]]

    def trending_top5(self):
        return self.trending_items()[0:5]

    def trending_hasmore(self):
        return bool(self.trending_items()[5:6])


class NewsSectionView(NewsMagazine):

    @property
    @memoize
    def section_id(self):
        return self.context.id

    @property
    @memoize
    def app(self):
        return self.context.aq_parent


class FeedItem(BrowserView):

    def can_edit(self):
        return api.user.has_permission('Modify',
                                       obj=self.context)

    def description(self, desc_len=160):
        return shorten(self.context.description, desc_len)

    def date(self):
        return self.context.effective().strftime('%B %d, %Y')

    def category(self):
        try:
            return self.context.section.to_object.title
        except AttributeError:
            return None


class NewsItemView(NewsMagazine):

    @property
    def section(self):
        try:
            return self.context.section.to_object
        except AttributeError:
            return None

    @property
    def section_id(self):
        if self.section:
            return self.section.id

    def date(self):
        return self.context.effective().strftime('%B %d, %Y')
