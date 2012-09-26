import itertools

from zope.interface import Interface
from zope.interface import implements
from zope.component import adapts
from zope.component import queryUtility
from zope.component import getMultiAdapter
from zope.app.component.hooks import getSite
from Acquisition import aq_inner
from AccessControl import Unauthorized
from AccessControl import getSecurityManager

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plonesocial.microblog.interfaces import IMicroblogTool
from plonesocial.activitystream.interfaces import IActivity

from .interfaces import IPlonesocialActivitystreamLayer
from .interfaces import IStreamProvider
from .interfaces import IActivityProvider


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
    plonesocial.networking @@profile
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
        # plonesocial.network @@profile renders this with a userid filter
        self.userid = None

    def update(self):
        pass

    def render(self):
        return self.index()

    __call__ = render

    def activities(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        if self.show_content or self.show_discussion:
            # fetch more than we need because of later filtering
            contentfilter = dict(sort_on='Date',
                                 sort_order='reverse',
                                 sort_limit=self.count * 10)
            if self.tag:
                contentfilter["Subject"] = self.tag
            if self.userid:
                contentfilter["Creator"] = self.userid
            brains = catalog.searchResults(**contentfilter)
        else:
            brains = []

        if self.show_microblog:
            container = queryUtility(IMicroblogTool)
            try:
                if self.userid:
                    # support plonesocial.network integration
                    statuses = container.user_values(self.userid,
                                                     limit=self.count,
                                                     tag=self.tag)
                else:
                    # default implementation
                    statuses = container.values(limit=self.count,
                                                tag=self.tag)
            except Unauthorized:
                statuses = []
        else:
            statuses = []

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

            if activity.is_status and self.show_microblog \
                    or activity.is_content and self.show_content \
                    or activity.is_discussion and self.show_discussion:
                yield activity
                i += 1

    def activity_providers(self):
        for activity in self.activities():
            if not self.can_view(activity):
                # discussion parent inaccessible
                continue
            yield getMultiAdapter(
                (activity, self.request, self.view),
                IActivityProvider,
                name="plonesocial.activitystream.activity_provider")

    def can_view(self, activity):
        """Returns true if current user has the 'View' permission.
        """
        sm = getSecurityManager()
        if activity.is_status:
            permission = "Plone Social: View Microblog Status Update"
            return sm.checkPermission(permission, self.context)
        elif activity.is_discussion:
            # check both the activity itself and it's page context
            return sm.checkPermission(
                'View', aq_inner(activity.context)) \
                and sm.checkPermission(
                    'View',
                    aq_inner(activity.context).__parent__.__parent__)
        elif activity.is_content:
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
