from zope.interface import implements
from zope.component import getMultiAdapter
from zope.publisher.interfaces import IPublishTraverse
from plone.app.layout.globals.interfaces import IViewView

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from profile import ProfileView


class AbstractGraph(ProfileView):
    implements(IPublishTraverse)

    index = ViewPageTemplateFile("templates/profile.pt")

    def miniprofile_provider(self, userid):
        provider = getMultiAdapter(
            (self.context, self.request, self),
            name="plonesocial.network.miniprofile_provider")
        provider.userid = userid
        return provider()


class FollowingView(AbstractGraph):

    implements(IPublishTraverse, IViewView)
    index = ViewPageTemplateFile("templates/graph.pt")
    Title = "Following"

    @property
    def description(self):
        return "%s is following:" % self.data['fullname']

    def users(self):
        return self.graph.get_following(self.userid)


class FollowersView(AbstractGraph):

    implements(IPublishTraverse, IViewView)
    index = ViewPageTemplateFile("templates/graph.pt")
    Title = "Followers"

    @property
    def description(self):
        return "%s is followed by:" % self.data['fullname']

    def users(self):
        return self.graph.get_followers(self.userid)
