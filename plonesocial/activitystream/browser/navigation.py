from zope.interface import implements
from zope.viewlet.interfaces import IViewlet
from zope.publisher.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter

from plonesocial.activitystream.integration import PLONESOCIAL


class PloneSocialNavigation(BrowserView):
    """Provide toplevel navigation that spans plonesocial.activitystream
    and plonesocial.network.
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
        portal_state = getMultiAdapter(
            (self.context, self.request),
            name=u'plone_portal_state')
        return portal_state.portal_url()

    def items(self):
        menu = []
        m_context = PLONESOCIAL.context(self.context)
        if m_context:
            m_base = m_context.absolute_url() + '/'
            menu.extend([dict(url=m_base + '@@stream',
                              title=m_context.Title() + ' updates',
                              state='')])

        base = self.portal_url() + '/'
        menu.extend([dict(url=base + '@@stream',
                          title='Explore',
                          state='')])
        if PLONESOCIAL.network:
            menu.extend([dict(url=base + '@@stream/network',
                              title='My network',
                              state=''),
                         dict(url=base + '@@profile',
                              title='My profile',
                              state='')])
        for item in menu:
            if self.request.URL == item['url']:
                item['state'] = 'active'
        return menu
