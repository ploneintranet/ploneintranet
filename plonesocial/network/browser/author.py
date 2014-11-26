# -*- coding: utf-8 -*-
from .interfaces import IAuthorProvider
from .interfaces import IPlonesocialNetworkLayer
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.globals.interfaces import IViewView
from plonesocial.network.interfaces import INetworkGraph
from zope.component import ComponentLookupError
from zope.component import adapts
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.component.hooks import getSite
from zope.interface import Interface
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
import logging

logger = logging.getLogger('plonesocial.network.author')


class AbstractAuthor(object):

    def render(self):
        return self.index()

    __call__ = render

    @property
    def viewer_id(self):
        '''The guy looking at the author view'''
        return self.mtool.getAuthenticatedMember().getId()

    @property
    def data(self):
        return self.mtool.getMemberInfo(self.userid)

    @property
    def portrait(self):
        '''Mugshot.'''
        return self.mtool.getPersonalPortrait(self.userid)

    @property
    def is_anonymous(self):
        return self.mtool.isAnonymousUser()

    @property
    def is_mine(self):
        '''Is this my own author profile, or somebody else's?'''
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

    def author_url(self):
        return self.portal_url() + '/@@/author' + self.userid

    def following_url(self):
        return self.portal_url() + '/@@following/' + self.userid

    def followers_url(self):
        return self.portal_url() + '/@@followers/' + self.userid

    def following_count(self):
        return len(self.graph.get_following(self.userid))

    def followers_count(self):
        return len(self.graph.get_followers(self.userid))


class AbstractAuthorProvider(AbstractAuthor):

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = self.__parent__ = view
        self.userid = None  # will be set by calling view

    def __call__(self):
        userid = self.request.form.get('userid', None)

        # no form submission - just render
        if userid is None:
            return self.render()

        # each inline authorprovider has a different userid
        # process only the right form out of many
        if userid is not None and userid == self.userid:
            followaction = self.request.form.get('subunsub_follow', None)
            unfollowaction = self.request.form.get('subunsub_unfollow', None)
            if followaction:
                self.graph.set_follow(self.viewer_id, userid)
                logger.info('%s follows %s', self.viewer_id, userid)
            elif unfollowaction:
                self.graph.set_unfollow(self.viewer_id, userid)
                logger.info('%s unfollowed %s', self.viewer_id, userid)
            # clear post data so users can reload - only on processed submit
            if followaction or unfollowaction:
                self.request.response.redirect(self.request.URL)
                return ''

        # the form submission was not ours, just render
        return self.render()


class MaxiAuthorProvider(AbstractAuthorProvider):

    implements(IAuthorProvider)
    adapts(Interface, IPlonesocialNetworkLayer, Interface)

    index = ViewPageTemplateFile('templates/maxiauthor_provider.pt')


class MiniAuthorProvider(AbstractAuthorProvider):

    implements(IAuthorProvider)
    adapts(Interface, IPlonesocialNetworkLayer, Interface)

    index = ViewPageTemplateFile('templates/miniauthor_provider.pt')


class AuthorView(BrowserView, AbstractAuthor):
    implements(IPublishTraverse, IViewView)

    index = ViewPageTemplateFile('templates/author.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self._userid = None

    def publishTraverse(self, request, name):
        ''' used for traversal via publisher, i.e. when using as a url '''
        self._userid = name
        return self

    @property
    def userid(self):
        '''The guy in the author'''
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
                name='plonesocial.activitystream.stream_provider')
            provider.users = self.userid
            return provider()
        except ComponentLookupError:
            # no plonesocial.activitystream available
            return ''

    def maxiauthor_provider(self, userid):
        provider = getMultiAdapter(
            (self.context, self.request, self),
            name='plonesocial.network.maxiauthor_provider')
        provider.userid = userid
        return provider()
