# coding=utf-8
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.memoize.view import memoize
from plone.tiles import Tile
from ploneintranet import api as piapi
from ploneintranet.activitystream.interfaces import IActivity
from ploneintranet.activitystream.interfaces import IStatusActivityReply
from ploneintranet.userprofile.content.userprofile import IUserProfile
import logging

logger = logging.getLogger(__name__)


class StreamTile(Tile):
    '''Tile view similar to StreamView.'''

    index = ViewPageTemplateFile("templates/stream_tile.pt")
    count = 15

    def __init__(self, context, request):
        self.context = context
        self.request = request
        # BBB: the or None should be moved to the microblog methods
        self.tag = self.data.get('tag') or None
        self.explore = 'network' not in self.data
        if 'last_seen' in request:
            self.last_seen = request.get('last_seen')
        else:
            self.last_seen = None
        self.stop_asking = False

    @property
    def next_max(self):
        if self.last_seen:
            return long(self.last_seen) - 1
        else:
            return None

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
        return piapi.microblog.get_microblog_context(self.context)

    def filter_statusupdates(self, statusupdates):
        ''' This method filters the microblog StatusUpdates

        The idea is:
         - if a StatusUpdate is a comment return the parent StatusUpdate
         - do not return duplicate statusupdates
        '''
        seen_thread_ids = set()
        good_statusupdates = []
        container = piapi.microblog.get_microblog()

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
        container = piapi.microblog.get_microblog()

        if self.microblog_context:
            # support ploneintranet.workspace integration
            statusupdates = container.context_values(
                self.microblog_context,
                max=self.next_max,
                limit=self.count,
                tag=self.tag
            )
        elif IUserProfile.providedBy(self.context):
            # Get the updates for this user
            statusupdates = container.user_values(
                self.context.username,
                max=self.next_max,
                limit=self.count,
                tag=self.tag
            )
        else:
            # default implementation
            statusupdates = container.values(
                max=self.next_max,
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
        for su in statusupdates:
            yield IActivity(su)

        # stop autoexpand when last batch is empty
        if len(statusupdates) == 0:
            self.stop_asking = True
        else:
            # last su when exiting loop
            self.last_seen = su.id

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
