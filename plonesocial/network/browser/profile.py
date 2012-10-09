from zope.interface import implements, Interface
from zope.component import adapts
from zope.component import getMultiAdapter, ComponentLookupError
from zope.component import queryUtility
from zope.publisher.interfaces import IPublishTraverse
from zope.app.component.hooks import getSite
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.globals.interfaces import IViewView

from plonesocial.network.interfaces import INetworkGraph
from .interfaces import IPlonesocialNetworkLayer
from .interfaces import IProfileProvider


class AbstractProfile(object):

    def render(self):
        return self.index()

    __call__ = render

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

    def portal_url(self):
        portal_state = getMultiAdapter(
            (self.context, self.request),
            name=u'plone_portal_state')
        return portal_state.portal_url()

    def profile_url(self):
        return self.portal_url() + "/@@profile/" + self.userid

    def following_url(self):
        return self.portal_url() + "/@@following/" + self.userid

    def followers_url(self):
        return self.portal_url() + "/@@followers/" + self.userid

    def following_count(self):
        return len(self.graph.get_following(self.userid))

    def followers_count(self):
        return len(self.graph.get_followers(self.userid))


class AbstractProfileProvider(AbstractProfile):

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = self.__parent__ = view
        self.userid = None  # will be set by calling view

    def __call__(self):
        if self.request.get('REQUEST_METHOD', 'GET').upper() == 'POST':
            action = self.request.form.get("subunsub", None)
            userid = self.request.form.get("userid", '')
            if action == 'follow' and userid == self.userid:
                self.graph.set_follow(self.viewer_id, userid)
            elif action == 'unfollow' and userid == self.userid:
                self.graph.set_unfollow(self.viewer_id, userid)
            # clear post data so users can reload
            self.request.response.redirect(self.request.URL)
            return ''
        return self.render()


class MaxiProfileProvider(AbstractProfileProvider):

    implements(IProfileProvider)
    adapts(Interface, IPlonesocialNetworkLayer, Interface)

    index = ViewPageTemplateFile("templates/maxiprofile_provider.pt")


class MiniProfileProvider(AbstractProfileProvider):

    implements(IProfileProvider)
    adapts(Interface, IPlonesocialNetworkLayer, Interface)

    index = ViewPageTemplateFile("templates/miniprofile_provider.pt")


class ProfileView(BrowserView, AbstractProfile):
    implements(IPublishTraverse, IViewView)

    index = ViewPageTemplateFile("templates/profile.pt")

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self._userid = None

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
            provider.users = self.userid
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
