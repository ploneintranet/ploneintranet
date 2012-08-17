from zope.interface import Interface
from zope.interface import implements
from zope.component import adapts
#from zope.component import getMultiAdapter
from zope.app.component.hooks import getSite

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from .interfaces import IPlonesocialActivitystreamLayer
from .interfaces import IStreamProvider


class StreamProvider(object):
    """Render activitystreams
    """
    implements(IStreamProvider)
    adapts(Interface, IPlonesocialActivitystreamLayer, Interface)

    index = ViewPageTemplateFile("templates/stream_provider.pt")

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.__parent__ = view

    def update(self):
        pass

    def render(self):
        return self.index()

    __call__ = render

    def is_anonymous(self):
        portal_membership = getToolByName(getSite(),
                                          'portal_membership',
                                          None)
        return portal_membership.isAnonymousUser()
