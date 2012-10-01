from zope.interface import implements
from zope.component import getMultiAdapter
from zope.component import ComponentLookupError
from zope.component import queryUtility
from zope.publisher.interfaces import IPublishTraverse
from zope.app.component.hooks import getSite
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plonesocial.network.interfaces import INetworkGraph


class AbstractGraph(BrowserView):
    implements(IPublishTraverse)

    index = ViewPageTemplateFile("templates/profile.pt")

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self._userid = None

    def __call__(self):
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

    @property
    def mtool(self):
        return getToolByName(getSite(), 'portal_membership')

    @property
    def graph(self):
        return queryUtility(INetworkGraph)

    def users(self):
        users = []
        for userid in self._users():
            userdata = self.mtool.getMemberInfo(userid)
            userdata['portrait'] = self.mtool.getPersonalPortrait(userid)
            users.append(userdata)
        return users


class FollowingView(AbstractGraph):

    implements(IPublishTraverse)
    index = ViewPageTemplateFile("templates/graph.pt")
    Title = "Following"

    def _users(self):
        return self.graph.get_following(self.userid)


class FollowersView(AbstractGraph):

    implements(IPublishTraverse)
    index = ViewPageTemplateFile("templates/graph.pt")
    Title = "Followers"

    def _users(self):
        return self.graph.get_followers(self.userid)
