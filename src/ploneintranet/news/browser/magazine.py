# -*- coding: utf-8 -*-
from .utils import obj2dict
from collective.mustread.interfaces import ITracker
from plone import api
from plone.memoize.view import memoize
from ploneintranet.async.tasks import MarkRead
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.core.i18nl10n import ulocalized_time
from ploneintranet.layout.utils import shorten
from Products.Five.browser import BrowserView
from sqlalchemy.exc import OperationalError
from zope.component import getUtility

import logging


log = logging.getLogger(__name__)


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
        try:
            # raises only on iterating generator
            most_read = [x for x in tracker.most_read(days=14)]
        except OperationalError:  # db error. happens in tests.
            log.error('Cannot retrieve trending items. Skipping.')
            most_read = []
        for item in most_read:  # sorted by most read desc
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
        return ulocalized_time(
            self.context.effective(), long_format=1,
            formatstring_domain='ploneintranet', context=self.context)

    def category(self):
        try:
            return self.context.section.to_object.title
        except AttributeError:
            return None

    def get_img_style(self, scale='mini'):
        ''' Return the style for the image tag
        '''
        return 'background-image: url({url}/@@images/image/{scale})'.format(
            scale=scale,
            url=self.context.absolute_url(),
        )

    def render(self, scale='mini'):
        ''' Call the index passing the scale as an option
        '''
        return self.index(scale=scale)


class NewsItemView(NewsMagazine):

    @property
    @memoize
    def app(self):
        return self.context.aq_parent

    @property
    @memoize
    def section(self):
        return self.context.section and self.context.section.to_object

    def date(self):
        return ulocalized_time(
            self.context.effective(), long_format=1,
            formatstring_domain='ploneintranet', context=self.context)

    def __call__(self):
        MarkRead(self.context, self.request)()
        return super(NewsItemView, self).__call__()
