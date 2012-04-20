from zope.interface import implements
from zope.viewlet.interfaces import IViewlet
from zope.publisher.browser import BrowserView
from Products.Five.browser.pagetemplatefile import \
    ViewPageTemplateFile


class Stream(BrowserView):
    """Integrated activity stream"""
    implements(IViewlet)

    def __init__(self, context, request, view, manager):
        self.context = context
        self.request = request
        self.__parent__ = view  # from IContentProvider
        self.manager = manager  # from IViewlet

    def update(self):
        pass

    render = ViewPageTemplateFile("templates/stream_viewlet.pt")
