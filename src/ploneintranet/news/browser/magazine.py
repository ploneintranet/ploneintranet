# -*- coding: utf-8 -*-
from collective.mustread.interfaces import ITracker
from Products.Five.browser import BrowserView
from plone import api
from ploneintranet.async.tasks import MarkRead
from ploneintranet.layout.utils import shorten
from plone.memoize.view import memoize
from zope.component import getUtility

from ploneintranet.core import ploneintranetCoreMessageFactory as _
from .utils import obj2dict


class NewsMagazine(BrowserView):

    section = None

    @property
    @memoize
    def app(self):
        return self.context

    @memoize
    def sections(self):
        # TODO: add 'trending'
        app_current = self.section is None
        sections = [dict(title=_('All news'),
                         absolute_url=self.app.absolute_url(),
                         css_class=app_current and 'current' or '')]
        for section in self.app.sections():
            if not section.section_visible:
                continue
            current = self.section == section
            css_class = current and 'current' or ''
            sections.append(obj2dict(
                section,
                'absolute_url', 'title',
                current=current, css_class=css_class
            ))
        return sections

    @memoize
    def news_items(self):
        items = []
        for item in self.app.news_items(self.section):
            if api.content.get_state(item) != 'published':
                continue
            if not item.magazine_home and not self.section:
                continue
            items.append(obj2dict(item, counter=len(items)))
        return items

    @memoize
    def trending_items(self, limit=None):
        news_objs = [x['obj'] for x in self.news_items()]
        leading = news_objs[:4]
        tracker = getUtility(ITracker)
        trending = []
        for item in tracker.most_read(days=14):  # sorted by most read desc
            # re-use effective/workflow/display filters of self.news_items
            if item not in news_objs:
                continue
            # do not show 4 topmost magazine items twice
            if item in leading:
                continue
            trending.append(obj2dict(item, counter=len(trending)))
            if len(trending) == limit:
                break
        return trending

    def trending_top5(self):
        return self.trending_items(5)

    def trending_hasmore(self):
        # return bool(self.trending_items()[5:6])
        # design is incomplete, not implemented
        return False


class NewsSectionView(NewsMagazine):

    @property
    @memoize
    def app(self):
        return self.context.aq_parent

    @property
    @memoize
    def section(self):
        return self.context


class FeedItem(BrowserView):

    @property
    @memoize
    def portal_url(self):
        return api.portal.get().absolute_url()

    def can_edit(self):
        return api.user.has_permission('Modify portal content',
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
    @memoize
    def app(self):
        return self.context.aq_parent

    @property
    @memoize
    def section(self):
        return self.context.section.to_object

    def date(self):
        return self.context.effective().strftime('%B %d, %Y')

    def __call__(self):
        MarkRead(self.context, self.request)()
        return super(NewsItemView, self).__call__()
