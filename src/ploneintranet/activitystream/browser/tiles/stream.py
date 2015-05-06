# coding=utf-8
from ..interfaces import IActivityProvider
from AccessControl import Unauthorized
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.memoize.view import memoize
from plone.tiles import Tile
from ploneintranet.activitystream.interfaces import IActivity
from ploneintranet.activitystream.interfaces import IStatusActivityReply
from ploneintranet.core.integration import PLONEINTRANET
from zExceptions import NotFound
from zope.component import getMultiAdapter
import logging

logger = logging.getLogger(__name__)


class StreamTile(Tile):
    """Tile view similar to StreamView."""

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

    def filter_microblog_activities(self, activities):
        """ BBB: this should really go in to PLONEINTRANET.microblog!

        We should get the activity already filtered
        """
        # For a reply IStatusActivity we render the parent post and then
        # all the replies are inside that. So, here we filter out reply who's
        # parent post we already rendered.
        seen_thread_ids = []
        good_activities = []

        container = PLONEINTRANET.microblog

        for activity in activities:
            if activity.thread_id and activity.thread_id in seen_thread_ids:
                continue
            elif activity.id in seen_thread_ids:
                continue

            if IStatusActivityReply.providedBy(activity):
                activity = container.get(activity.thread_id)

            seen_thread_ids.append(activity.id)
            good_activities.append(activity)

        return good_activities

    def get_microblog_activities(self):
        ''' This will return all the StatusActivity which are not replies
        '''
        container = PLONEINTRANET.microblog

        if self.microblog_context:
            # support collective.local integration
            activities = container.context_values(
                self.microblog_context,
                limit=self.count,
                tag=self.tag
            )
        else:
            # default implementation
            activities = container.values(
                limit=self.count,
                tag=self.tag
            )
        activities = self.filter_microblog_activities(activities)
        return activities

    @property
    @memoize
    def activities(self):
        ''' The list of our activities
        '''
        items = self.get_microblog_activities()
        # see date_key sorting function above
        items = sorted(items, key=lambda x: x.date, reverse=True)

        i = 0
        for item in items:
            if i >= self.count:
                break
            try:
                activity = IActivity(item)
            except Unauthorized:
                continue
            except NotFound:
                logger.exception("NotFound: %s" % item.getURL())
                continue

            activity_provider = getMultiAdapter(
                (activity, self.request, self),
                IActivityProvider
            )
            yield activity_provider
            i += 1

    @memoize
    def activity_providers(self):
        ''' Return the activity providers
        '''
        return tuple(self.activities)

    def activity_as_post(self, activity):
        ''' BBB: just for testing
        '''
        return api.content.get_view(
            'activity_view',
            activity.context,
            self.request
        ).as_post()

    def activity_views(self):
        ''' The activity as views
        '''
        return [
            api.content.get_view(
                'activity_view',
                activity.context,
                self.request
            ).as_post
            for activity in self.activity_providers()
        ]
