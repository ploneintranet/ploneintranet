from zope.interface import implements
from zope.viewlet.interfaces import IViewlet
from zope.publisher.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter

from ploneintranet.core.integration import PLONEINTRANET


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
        portal_state = getMultiAdapter(
            (self.context, self.request),
            name=u'plone_portal_state')
        return portal_state.portal_url()

    def items(self):
        menu = []
        m_context = PLONEINTRANET.context(self.context)
        if m_context:
            m_base = m_context.absolute_url() + '/'
            menu.extend([dict(url=m_base + '@@stream',
                              title=m_context.Title() + ' updates',
                              state='localstream')])

        base = self.portal_url() + '/'
        menu.extend([dict(url=base + '@@stream',
                          title='Explore',
                          state='explore')])
        if PLONEINTRANET.network:
            menu.extend([dict(url=base + '@@stream/network',
                              title='My network',
                              state='stream'),
                         dict(url=base + '@@author',
                              title='My profile',
                              state='profile')])
        for item in menu:
            if self.request.URL == item['url']:
                item['state'] = 'active'
        return menu
