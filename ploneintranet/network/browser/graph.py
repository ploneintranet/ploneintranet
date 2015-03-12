# -*- coding: utf-8 -*-
from .author import AuthorView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.globals.interfaces import IViewView
from ploneintranet.network import _
from zope.component import getMultiAdapter
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


class AbstractGraph(AuthorView):
    implements(IPublishTraverse)

    index = ViewPageTemplateFile('templates/author.pt')

    def miniauthor_provider(self, userid):
        provider = getMultiAdapter(
            (self.context, self.request, self),
            name='ploneintranet.network.miniauthor_provider')
        provider.userid = userid
        return provider()


class FollowingView(AbstractGraph):

    implements(IPublishTraverse, IViewView)
    index = ViewPageTemplateFile('templates/graph.pt')
    Title = _(u'Following')

    @property
    def description(self):
        # TODO check this string, by extract it for add i18n support
        return _(u'%s is following:') % self.data['fullname']

    def users(self):
        return self.graph.get_following(self.userid)


class FollowersView(AbstractGraph):

    implements(IPublishTraverse, IViewView)
    index = ViewPageTemplateFile('templates/graph.pt')
    Title = _(u'Followers')

    @property
    def description(self):
        # TODO check this string, by extract it for add i18n support
        return _(u'%s is followed by:') % self.data['fullname']

    def users(self):
        return self.graph.get_followers(self.userid)
