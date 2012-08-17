from zope.interface import implements
from zope.component import getMultiAdapter
from zope.formlib import form
from Acquisition import aq_inner

from plone.app.portlets.portlets import base
from zope.viewlet.interfaces import IViewlet
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from .interfaces import IActivitystreamPortlet

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
        pass

    def stream_provider(self):
        provider = getMultiAdapter(
            (self.context, self.request, self.view),
            name="plonesocial.activitystream.stream_provider")
        provider.portlet_data = self.data
        return provider()


class AddForm(base.AddForm):
    form_fields = form.Fields(IActivitystreamPortlet)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    form_fields = form.Fields(IActivitystreamPortlet)
