# coding=utf-8
from AccessControl import Unauthorized
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.memoize.view import memoize
from plone.tiles import Tile
from ploneintranet.activitystream.interfaces import IActivity
from ploneintranet.activitystream.interfaces import IStatusActivityReply
from ploneintranet.core.integration import PLONEINTRANET
from zExceptions import NotFound
import logging

logger = logging.getLogger(__name__)


class StreamTile(Tile):
    '''Tile view similar to StreamView.'''

    index = ViewPageTemplateFile("templates/stream_tile.pt")
    count = 15

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.tag = self.data.get('tag')
        self.explore = 'network' not in self.data

    @memoize
    def is_anonymous(self):
        return api.user.is_anonymous()

    @property
    @memoize
    def toLocalizedTime(self):
        ''' Facade for the toLocalizedTime method
        '''
        return api.portal.get_tool('translation_service').toLocalizedTime

    @property
    @memoize
    def microblog_context(self):
        ''' Returns the microblog context
        '''
        return PLONEINTRANET.context(self.context)

    def filter_statusupdates(self, statusupdates):
        ''' This method filters the microblog StatusUpdates

        The idea is:
         - if a StatusUpdate is a comment return the parent StatusUpdate
         - do not return duplicate statusupdates
        '''
        seen_thread_ids = set()
        good_statusupdates = []
        container = PLONEINTRANET.microblog

        for su in statusupdates:
            if su.thread_id and su.thread_id in seen_thread_ids:
                continue
            elif su.id in seen_thread_ids:
                continue

            if IStatusActivityReply.providedBy(su):
                su = container.get(su.thread_id)

            seen_thread_ids.add(su.id)
            good_statusupdates.append(su)

        return good_statusupdates

    def get_statusupdates(self):
        ''' This will return all the StatusUpdates which are not comments

        The activity are sorted by reverse chronological order
        '''
        container = PLONEINTRANET.microblog

        if self.microblog_context:
            # support collective.local integration
            statusupdates = container.context_values(
                self.microblog_context,
                limit=self.count,
                tag=self.tag
            )
        else:
            # default implementation
            statusupdates = container.values(
                limit=self.count,
                tag=self.tag
            )
        statusupdates = self.filter_statusupdates(statusupdates)
        return statusupdates

    @property
    @memoize
    def activities(self):
        ''' The list of our activities
        '''
        statusupdates = self.get_statusupdates()
        i = 0
        for su in statusupdates:
            if i >= self.count:
                break
            try:
                activity = IActivity(su)
            except Unauthorized:
                continue
            except NotFound:
                logger.exception("NotFound: %s" % activity.getURL())
                continue

            yield activity
            i += 1

    @property
    @memoize
    def activity_views(self):
        ''' The activity as views
        '''
        return [
            api.content.get_view(
                'activity_view',
                activity,
                self.request
            ).as_post
            for activity in self.activities
        ]
