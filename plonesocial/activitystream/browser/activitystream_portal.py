import itertools

from zope.interface import implements
from zope.component import queryUtility
from zope.component import getMultiAdapter
from zope.formlib import form
from Acquisition import aq_inner
from AccessControl import Unauthorized
from AccessControl import getSecurityManager

from Products.CMFCore.utils import getToolByName

from plone.app.portlets.portlets import base
from zope.viewlet.interfaces import IViewlet
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plonesocial.microblog.interfaces import IMicroblogTool
from plonesocial.activitystream.interfaces import IActivity
from plonesocial.activitystream.browser.interfaces \
    import IActivitystreamPortlet
from plonesocial.activitystream.browser.interfaces \
    import IActivityProvider

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('plonesocial.activitystream')


class PortalView(BrowserView):
    """Home page view containing activity stream viewlets."""

    index = ViewPageTemplateFile("templates/activitystream_portal.pt")

    def render(self):
        return self.index()

    def __call__(self):
        return self.render()

    def update(self):
        """Mute plone.app.z3cform.kss.validation AttributeError"""
        pass


class PortletManagerViewlet(BrowserView):
    """Viewlet that acts as a portlet manager.
    Deletates actual activity stream rendering to a portlet,
    so that content managers can easily set preferences.
    """
    implements(IViewlet)

    def __init__(self, context, request, view, manager):
        self.context = context
        self.request = request
        self.__parent__ = view  # from IContentProvider
        self.manager = manager  # from IViewlet

    def update(self):
        pass

    render = ViewPageTemplateFile(
        "templates/activitystream_portletmanager_viewlet.pt")


## activitystream_portlet below


class Assignment(base.Assignment):
    implements(IActivitystreamPortlet)

    title = u""  # overrides readonly property method from base class

    def __init__(self,
                 title='Activity Stream',
                 count=5,
                 compact=True,
                 show_microblog=True,
                 show_content=True,
                 show_discussion=True):
        self.title = title
        self.count = count
        self.compact = compact
        self.show_microblog = show_microblog
        self.show_content = show_content
        self.show_discussion = show_discussion


class Renderer(base.Renderer):

    render = ViewPageTemplateFile('templates/activitystream_portlet.pt')

    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)
        self.items = []

    @property
    def available(self):
        return True

    @property
    def compact(self):
        return self.data.compact

    @property
    def portal_url(self):
        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request),
                                       name=u'plone_portal_state')
        return portal_state.portal_url()

    def update(self):
        tag = self.request.get('tag', None)
        catalog = getToolByName(self.context, 'portal_catalog')
        if self.data.show_content or self.data.show_discussion:
            # fetch more than we need because of later filtering
            contentfilter = dict(sort_on='Date',
                                 sort_order='reverse',
                                 sort_limit=self.data.count * 10)
            if tag:
                contentfilter["Subject"] = tag
            brains = catalog.searchResults(**contentfilter)
        else:
            brains = []

        if self.data.show_microblog:
            container = queryUtility(IMicroblogTool)
            try:
                statuses = container.values(limit=self.data.count,
                                            tag=tag)
            except Unauthorized:
                statuses = []
        else:
            statuses = []

        activities = itertools.chain(brains, statuses)

        def date_key(item):
            if hasattr(item, 'effective'):
                # catalog brain
                return max(item.effective, item.created)
            # Activity
            return item.date

        activities = sorted(activities, key=date_key, reverse=True)

        self.items = []
        for item in activities:
            if len(self.items) >= self.data.count:
                break

            try:
                activity = IActivity(item)
            except Unauthorized:
                continue

            if activity.is_status and self.data.show_microblog \
                    or activity.is_content and self.data.show_content \
                    or activity.is_discussion and self.data.show_discussion:
                self.items.append(activity)

    def itemproviders(self):
        for item in self.items:
            if not self.can_view(item):
                # discussion parent inaccessible
                continue
            yield getMultiAdapter((item, self.request, self.view),
                                  IActivityProvider,
                                  name="activity_provider")

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


class AddForm(base.AddForm):
    form_fields = form.Fields(IActivitystreamPortlet)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    form_fields = form.Fields(IActivitystreamPortlet)
