from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from ploneintranet import api as piapi
from zope.interface import implements
from zope.viewlet.interfaces import IViewlet
from zope.publisher.browser import BrowserView


class PloneIntranetNavigation(BrowserView):
    """Provide toplevel navigation that spans ploneintranet.activitystream
    and ploneintranet.network.
    """
    implements(IViewlet)

    def __init__(self, context, request, view, manager):
        self.context = context
        self.request = request
        self.view = self.__parent__ = view
        self.manager = manager

    def update(self):
        pass

    render = ViewPageTemplateFile("templates/navigation.pt")

    def portal_url(self):
        portal_state = api.content.get_view(
            u'plone_portal_state',
            self.context,
            self.request,
        )
        return portal_state.portal_url()

    def items(self):
        menu = []
        m_context = piapi.microblog.get_microblog_context(self.context)
        if m_context:
            m_base = m_context.absolute_url() + '/'
            menu.extend([dict(url=m_base + '@@stream',
                              title=m_context.Title() + ' updates',
                              state='localstream')])

        for item in menu:
            if self.request.URL == item['url']:
                item['state'] = 'active'
        return menu
