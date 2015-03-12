import itertools

from zope.interface import Interface
from zope.interface import implements
from zope.component import adapts
from zope.component import getMultiAdapter
from zope.component.hooks import getSite

from Acquisition import aq_inner
from AccessControl import Unauthorized
from AccessControl import getSecurityManager
from zExceptions import NotFound

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from ploneintranet.activitystream.interfaces import IActivity

from .interfaces import IPlonesocialActivitystreamLayer
from .interfaces import IStreamProvider
from .interfaces import IActivityProvider

from ploneintranet.activitystream.interfaces import IStatusActivity
from ploneintranet.activitystream.interfaces import IStatusActivityReply
from ploneintranet.activitystream.interfaces import IContentActivity
from ploneintranet.activitystream.interfaces import IDiscussionActivity

from ploneintranet.core.integration import PLONEINTRANET

import logging

logger = logging.getLogger(__name__)


def date_key(item):
    if hasattr(item, 'effective'):
        # catalog brain
        return max(item.effective, item.created)
    # Activity
    return item.date


class StreamProvider(object):
    """Render activitystreams

    This is the core rendering logic that powers
    @@stream and @@activitystream_portal, and also
    ploneintranet.networking @@author
    """
    implements(IStreamProvider)
    adapts(Interface, IPlonesocialActivitystreamLayer, Interface)

    index = ViewPageTemplateFile("templates/stream_provider.pt")

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = self.__parent__ = view
        # @@activitystream_portal renders this as a portlet
        self.portlet_data = None
        # @@stream renders this optionally with a tag filter
        self.tag = None
        # @@stream and ploneintranet.network:@@author
        # render this optionally with a users filter
        self.users = None
        self.microblog_context = PLONEINTRANET.context(context)

    def update(self):
        pass

    def render(self):
        return self.index()

    __call__ = render

    def activities(self):
        brains = self._activities_brains()
        statuses = self._activities_statuses()
        items = itertools.chain(brains, statuses)
        # see date_key sorting function above
        items = sorted(items, key=date_key, reverse=True)

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

            if self._activity_visible(activity):
                yield activity
                i += 1

    def _activity_visible(self, activity):
        if IStatusActivity.providedBy(activity) and self.show_microblog:
            return True
        elif IContentActivity.providedBy(activity) and self.show_content:
            return True
        elif IDiscussionActivity.providedBy(activity) and self.show_discussion:
            return True

        return False

    def _activities_brains(self):
        if not self.show_content and not self.show_discussion:
            return []
        catalog = getToolByName(self.context, 'portal_catalog')
        # fetch more than we need because of later filtering
        contentfilter = dict(sort_on='Date',
                             sort_order='reverse',
                             sort_limit=self.count * 10)
        if self.tag:
            contentfilter["Subject"] = self.tag
        # filter on users OR context, not both
        if self.users:
            contentfilter["Creator"] = self.users
        elif self.microblog_context:
            contentfilter['path'] = \
                '/'.join(self.microblog_context.getPhysicalPath())

        return catalog.searchResults(**contentfilter)

    def _activities_statuses(self):
        if not self.show_microblog:
            raise StopIteration()
        container = PLONEINTRANET.microblog
        # show_microblog yet no container can happen on microblog uninstall
        if not container:
            raise StopIteration()

        # filter on users OR context, not both
        if self.users:
            # support ploneintranet.network integration
            activities = container.user_values(self.users,
                                               limit=self.count,
                                               tag=self.tag)
        elif self.microblog_context:
            # support collective.local integration
            activities = container.context_values(self.microblog_context,
                                                  limit=self.count,
                                                  tag=self.tag)
        else:
            # default implementation
            activities = container.values(limit=self.count, tag=self.tag)

        # For a reply IStatusActivity we render the parent post and then
        # all the replies are inside that. So, here we filter out reply who's
        # parent post we already rendered.
        seen_thread_ids = []
        for activity in activities:
            if (activity.thread_id and activity.thread_id in seen_thread_ids) \
                    or activity.id in seen_thread_ids:
                continue

            if IStatusActivityReply.providedBy(activity):
                seen_thread_ids.append(activity.thread_id)
            else:
                seen_thread_ids.append(activity.id)

            yield activity

    def activity_providers(self):
        for activity in self.activities():
            if not self.can_view(activity):
                # discussion parent inaccessible
                continue

            yield getMultiAdapter(
                (activity, self.request, self.view),
                IActivityProvider)

    def can_view(self, activity):
        """Returns true if current user has the 'View' permission.
        """
        sm = getSecurityManager()
        if IStatusActivity.providedBy(activity):
            permission = "Plone Social: View Microblog Status Update"
            return sm.checkPermission(permission, self.context)
        elif IDiscussionActivity.providedBy(activity):
            # check both the activity itself and it's page context
            return sm.checkPermission(
                'View', aq_inner(activity.context)) \
                and sm.checkPermission(
                    'View',
                    aq_inner(activity.context).__parent__.__parent__)
        elif IContentActivity.providedBy(activity):
            return sm.checkPermission('View',
                                      aq_inner(activity.context))

    def is_anonymous(self):
        portal_membership = getToolByName(getSite(),
                                          'portal_membership',
                                          None)
        return portal_membership.isAnonymousUser()

    @property
    def count(self):
        if self.portlet_data:
            return self.portlet_data.count
        return 15

    @property
    def show_microblog(self):
        sm = getSecurityManager()
        permission = "Plone Social: View Microblog Status Update"
        if not sm.checkPermission(permission, self.context):
            return False
        if self.portlet_data:
            return self.portlet_data.show_microblog
        return True

    @property
    def show_content(self):
        if self.portlet_data:
            return self.portlet_data.show_content
        return True

    @property
    def show_discussion(self):
        if self.portlet_data:
            return self.portlet_data.show_discussion
        return True
