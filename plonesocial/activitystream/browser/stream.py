from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('plonesocial.activitystream')


class StreamView(BrowserView):
    """Standalone view, providing
    - microblog input
    - activitystream rendering (via stream provider)

    @@stream -> either: all activities, or
             -> my network activities (if plonesocial.network is installed)
    @@stream/explore -> all activities (if plonesocial.network is installed)
    @@stream/tag/foobar -> all activities tagged #foobar
    """

    implements(IPublishTraverse)

    index = ViewPageTemplateFile("templates/stream.pt")

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.tag = None

    def render(self):
        return self.index()

    def __call__(self):
        return self.render()

    def update(self):
        """Mute plone.app.z3cform.kss.validation AttributeError"""
        pass

    def publishTraverse(self, request, name):
        """ used for traversal via publisher, i.e. when using as a url """
        if name == 'tag':
            stack = request.get('TraversalRequestNameStack')
            self.tag = stack.pop()
        return self
