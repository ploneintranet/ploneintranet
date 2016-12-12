# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from plone import api
from plone.memoize.view import memoize
from ploneintranet.layout.utils import shorten
from Products.CMFPlone import PloneMessageFactory as _pmf
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.relationfield import RelationValue
from zope import component
from zope.intid.interfaces import IIntIds

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
            news_items = self.news_items(section)
            delete_protected = len(news_items) > 0
            has_more = len(news_items) == 5
            _sections.append(obj2dict(
                section,
                'id', 'title', 'description', 'absolute_url',
                news_items=news_items,
                delete_protected=delete_protected,
                has_more=has_more,
            ))
        if len(_sections) == 1:
            _sections[0]['delete_protected'] = True
        return _sections

    @memoize
    def news_items(self, section=None, start=None, limit=5):
        desc_len = 160
        _items = []
        i = 0
        for item in self.context.news_items(section, start, limit,
                                            sort_on='created',
                                            sort_order='reverse'):
            i += 1
            if item.section:
                category = item.section.to_object.title
            else:
                category = None
            published = api.content.get_state(item) == 'published'
            _items.append(obj2dict(
                item,
                'id', 'title', 'absolute_url',
                description=shorten(item.description, desc_len),
                date=item.effective().strftime('%B %d, %Y'),
                category=category,
                counter=i,
                can_edit=api.user.has_permission('Modify', obj=item),
                published=published,
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
        visibility = get('item_visibility', 'both')
        if visibility == 'both':
            magazine_home = True
        else:
            magazine_home = False
        # always force a section - default to first in app
        section = self.context.sections()[0]
        intids = component.getUtility(IIntIds)
        item = api.content.create(
            container=self.context,
            type='News Item',
            title=title,
            description=description,
            section=RelationValue(intids.getId(section)),
            magazine_home=magazine_home,
        )
        item.indexObject()
        log.info("Created news item {}".format(item))


class SectionMore(NewsPublisher):

    @memoize
    def more_items(self):
        return self.news_items(section=self.context, start=5, limit=None)


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

    def app_url(self):
        return self.app.absolute_url()

    def sidebar(self):
        publisher = api.content.get_view('publisher', self.app, self.request)
        return publisher.sidebar()

    def can_review(self):
        return api.user.has_permission('Review portal content',
                                       obj=aq_inner(self.context))

    def sections(self):
        _sections = []
        for section in self.app.sections():
            if self.context.section:
                context_section = self.context.section.to_object
            else:
                context_section = None
            current = section == context_section
            _sections.append(obj2dict(section,
                                      'title',
                                      current=current,
                                      uuid=section.uuid))
        return _sections

    def update(self):
        # do not remove existing image without new upload
        if 'image' in self.request.form.keys() \
           and not bool(self.request.form.get('image')):
            del(self.request.form['image'])
        return super(NewsItemEdit, self).update()

    @property
    def effective(self):
        return self.format_date(self.context.effective())

    @property
    def expires(self):
        return self.format_date(self.context.expires())

    def format_date(self, dt):
        date = dt.strftime('%Y-%m-%d')
        if date.startswith('20'):
            return date
        else:
            return ''


class NewsItemDelete(NewsItemEdit):

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
            return super(NewsItemDelete, self).__call__()

    def update(self):
        log.info("Deleting {}".format(self.context))
        title = safe_unicode(self.context.Title())
        api.content.delete(obj=self.context, check_linkintegrity=False)
        api.portal.show_message(
            _pmf(u'${title} has been deleted.', mapping={u'title': title}),
            request=self.request
        )
