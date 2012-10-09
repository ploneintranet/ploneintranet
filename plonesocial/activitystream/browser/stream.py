from zope.interface import implements
from zope.component import getMultiAdapter
from zope.publisher.interfaces import IPublishTraverse
from plone.app.layout.globals.interfaces import IViewView
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plonesocial.activitystream.integration import PLONESOCIAL

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

    implements(IPublishTraverse, IViewView)

    index = ViewPageTemplateFile("templates/stream.pt")

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.tag = None
        if not PLONESOCIAL.network:
            # no network, show all
            self.explore = True
        else:
            # have network, default to filter on following
            self.explore = False

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
        elif name == 'explore':
            # @@stream/explore disables 'following' filter
            self.explore = True
        return self

    def status_provider(self):
        if not PLONESOCIAL.microblog:
            return ''

        provider = getMultiAdapter(
            (self.context, self.request, self),
            name="plonesocial.microblog.status_provider")
        provider.update()
        return provider()

    def stream_provider(self):
        provider = getMultiAdapter(
            (self.context, self.request, self),
            name="plonesocial.activitystream.stream_provider")
        provider.tag = self.tag

        # explore -> no user filter
        if self.explore:
            return provider()

        # no valid user context -> no user filter
        mtool = getToolByName(self.context, 'portal_membership')
        viewer_id = mtool.getAuthenticatedMember().getId()
        if mtool.isAnonymousUser() or not viewer_id:
            return provider()

        # valid user context -> filter on following
        following = list(PLONESOCIAL.network.get_following(viewer_id))
        following.append(viewer_id)  # show own updates in stream
        provider.users = following
        return provider()
