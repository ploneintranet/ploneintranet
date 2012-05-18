from zope.interface import implements
from zope.viewlet.interfaces import IViewlet
from zope.publisher.browser import BrowserView
from Products.Five.browser.pagetemplatefile import \
    ViewPageTemplateFile


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

    render = ViewPageTemplateFile("templates/portletmanager_viewlet.pt")
