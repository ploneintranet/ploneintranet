# coding=utf-8
from ..interfaces import IActivityProvider
from AccessControl import Unauthorized
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.memoize.view import memoize
from plone.tiles import Tile
from ploneintranet.activitystream.browser.activity_provider import (
    StatusActivityReplyProvider
)
from ploneintranet.activitystream.interfaces import IActivity
from ploneintranet.activitystream.interfaces import IStatusActivity
from ploneintranet.activitystream.interfaces import IStatusActivityReply
from ploneintranet.core.integration import PLONEINTRANET
from zExceptions import NotFound
from zope.component import getMultiAdapter
import logging

logger = logging.getLogger(__name__)


class StreamTile(Tile):
    """Tile view similar to StreamView."""

    index = ViewPageTemplateFile("templates/stream_tile.pt")
    view_permission = "Plone Social: View Microblog Status Update"
    count = 15

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.tag = self.data.get('tag')
        self.explore = 'network' not in self.data

    @memoize
    def is_anonymous(self):
        return api.user.is_anonymous()

    @memoize
    def can_view(self):
        """Returns true if current user has the 'View' permission.
        """
        return api.user.has_permission(self.view_permission, obj=self.context)

    @property
    @memoize
    def microblog_context(self):
        ''' Returns the microblog context
        '''
        return PLONEINTRANET.context(self.context)

    def get_microblog_activities(self):
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

        # For a reply IStatusActivity we render the parent post and then
        # all the replies are inside that. So, here we filter out reply who's
        # parent post we already rendered.
        seen_thread_ids = []
        for activity in activities:
            if (
                (activity.thread_id and activity.thread_id in seen_thread_ids)
                or activity.id in seen_thread_ids
            ):
                continue

            if IStatusActivityReply.providedBy(activity):
                seen_thread_ids.append(activity.thread_id)
            else:
                seen_thread_ids.append(activity.id)
            yield activity

    @property
    @memoize
    def activities(self):
        ''' The list of our activities
        '''
        if not self.can_view():
            raise StopIteration()

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

            if IStatusActivity.providedBy(activity):
                yield getMultiAdapter(
                    (activity, self.request, self),
                    IActivityProvider
                )
                i += 1

    def activity_providers(self):
        ''' Return the activity providers
        '''
        activity_providers = self.activities
        # some of the activities are comment replies
        # in that case we should return the provider of the parent activity
        real_providers = []
        for activity_provider in activity_providers:
            if isinstance(activity_provider, StatusActivityReplyProvider):
                real_providers.append(activity_provider.parent_provider())
            else:
                real_providers.append(activity_provider)
        return real_providers
