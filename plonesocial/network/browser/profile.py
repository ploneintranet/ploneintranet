from zope.interface import implements, Interface
from zope.component import adapts
from zope.component import getMultiAdapter, ComponentLookupError
from zope.component import queryUtility
from zope.publisher.interfaces import IPublishTraverse
from zope.app.component.hooks import getSite
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plonesocial.network.interfaces import INetworkGraph
from .interfaces import IPlonesocialNetworkLayer
from .interfaces import IProfileProvider


class AbstractProfile(object):

    @property
    def viewer_id(self):
        """The guy looking at the profile"""
        return self.mtool.getAuthenticatedMember().getId()

    @property
    def data(self):
        return self.mtool.getMemberInfo(self.userid)

    @property
    def portrait(self):
        """Mugshot."""
        return self.mtool.getPersonalPortrait(self.userid)

    @property
    def is_anonymous(self):
        return self.mtool.isAnonymousUser()

    @property
    def is_mine(self):
        """Is this my own profile, or somebody else's?"""
        return self.userid == self.viewer_id

    @property
    def is_following(self):
        return self.userid in self.graph.get_following(self.viewer_id)

    @property
    def show_subunsub(self):
        return not(self.is_anonymous or self.is_mine)

    @property
    def mtool(self):
        return getToolByName(getSite(), 'portal_membership')

    @property
    def graph(self):
        return queryUtility(INetworkGraph)

    @property
    def profile_url(self):
        portal_state = getMultiAdapter(
            (self.context, self.request),
            name=u'plone_portal_state')
        return portal_state.portal_url() + "/@@profile/" + self.userid


class MaxiProfileProvider(AbstractProfile):

    implements(IProfileProvider)
    adapts(Interface, IPlonesocialNetworkLayer, Interface)

    __call__ = ViewPageTemplateFile("templates/maxiprofile_provider.pt")

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = self.__parent__ = view
        self.userid = None


class MiniProfileProvider(AbstractProfile):

    implements(IProfileProvider)
    adapts(Interface, IPlonesocialNetworkLayer, Interface)

    __call__ = ViewPageTemplateFile("templates/miniprofile_provider.pt")

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = self.__parent__ = view
        self.userid = None


class ProfileView(BrowserView, AbstractProfile):
    implements(IPublishTraverse)

    index = ViewPageTemplateFile("templates/profile.pt")

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self._userid = None

    def __call__(self):
        if self.request.get('REQUEST_METHOD', 'GET').upper() == 'POST':
            action = self.request.form.get("subunsub")
            if action == 'follow':
                self.graph.set_follow(self.viewer_id, self.userid)
            elif action == 'unfollow':
                self.graph.set_unfollow(self.viewer_id, self.userid)
            # clear post data so users can reload
            self.request.response.redirect(self.request.URL)
            return ''
        return self.render()

    def render(self):
        return self.index()

    def publishTraverse(self, request, name):
        """ used for traversal via publisher, i.e. when using as a url """
        self._userid = name
        return self

    @property
    def userid(self):
        """The guy in the profile"""
        if self._userid:
            return self._userid
        elif self.is_anonymous:
            return None
        else:
            return self.viewer_id

    def stream_provider(self):
        try:
            # plonesocial.activitystream integration is optional
            provider = getMultiAdapter(
                (self.context, self.request, self),
                name="plonesocial.activitystream.stream_provider")
            provider.userid = self.userid
            return provider()
        except ComponentLookupError:
            # no plonesocial.activitystream available
            return ''

    def maxiprofile_provider(self, userid):
        provider = getMultiAdapter(
            (self.context, self.request, self),
            name="plonesocial.network.maxiprofile_provider")
        provider.userid = userid
        return provider()
