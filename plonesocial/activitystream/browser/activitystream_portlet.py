import itertools

from zope.interface import implements
from zope.component import queryUtility

from zope import schema
from zope.formlib import form
from Acquisition import aq_inner
from AccessControl import Unauthorized
from AccessControl import getSecurityManager

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory as PMF
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter

from plonesocial.microblog.interfaces import IMicroblogTool
from plonesocial.activitystream.interfaces import IActivity
from plonesocial.activitystream.browser.interfaces \
    import IActivityContentProvider

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('plonesocial.activitystream')


class IActivitystreamPortlet(IPortletDataProvider):
    """A portlet to render the activitystream.
    """

    title = schema.TextLine(title=PMF(u"Title"),
                            description=_(u"A title for this portlet"),
                            required=True,
                            default=u"Activity Stream")

    count = schema.Int(
        title=_(u"Number of updates to display"),
        description=_(u"Maximum number of updates to show"),
        required=True,
        default=5)

    compact = schema.Bool(title=_(u"Compact rendering"),
                          description=_(u"Hide portlet header and footer"),
                          default=True)

    show_microblog = schema.Bool(
        title=_(u"Show microblog"),
        description=_(u"Show microblog status updates"),
        default=True)

    show_content = schema.Bool(
        title=_(u"Show content creation"),
        description=_(u"Show creation of new content"),
        default=True)

    show_discussion = schema.Bool(
        title=_(u"Show discussion"),
        description=_(u"Show discussion replies"),
        default=True)


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
        catalog = getToolByName(self.context, 'portal_catalog')
        if self.data.show_content or self.data.show_discussion:
            # fetch more than we need because of later filtering
            brains = catalog.searchResults(sort_on='effective',
                                           sort_order='reverse',
                                           sort_limit=self.data.count * 10,
                                           )
        else:
            brains = []

        if self.data.show_microblog:
            container = queryUtility(IMicroblogTool)
            try:
                statuses = container.values(limit=self.data.count)
            except Unauthorized:
                statuses = []
        else:
            statuses = []

        activities = itertools.chain(brains, statuses)

        def date_key(item):
            if hasattr(item, 'effective'):
                # catalog brain
                return item.effective
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
                                  IActivityContentProvider,
                                  name="activity_contentprovider")

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
