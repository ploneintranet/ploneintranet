# -*- coding: utf-8 -*-
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.app.blocks.interfaces import IBlocksTransformEnabled
from plone.app.layout.globals.interfaces import IViewView
from plonesocial.core import plonesocialCoreMessageFactory as _
from plonesocial.core.integration import PLONESOCIAL
from zope.component import getMultiAdapter
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


class StreamBase(object):

    '''Base for View and Tile'''

    def render(self):
        return self.index()

    def __call__(self):
        return self.render()

    def stream_provider(self):
        provider = getMultiAdapter(
            (self.context, self.request, self),
            name='plonesocial.core.stream_provider'
        )
        provider.tag = self.tag

        # explore or tag -> no user filter
        if self.explore or self.tag:
            return provider()

        # no valid user context -> no user filter
        mtool = api.portal.get_tool('portal_membership')
        viewer_id = mtool.getAuthenticatedMember().getId()
        if mtool.isAnonymousUser() or not viewer_id:
            return provider()

        # valid user context -> filter on following
        following = list(PLONESOCIAL.network.get_following(viewer_id))
        following.append(viewer_id)  # show own updates in stream
        provider.users = following
        return provider()


class StreamView(StreamBase, BrowserView):

    '''Standalone view, providing
    - microblog input
    - activitystream rendering (via stream provider)

    @@stream -> either: all activities, or
             -> my network activities (if plonesocial.network is installed)
    @@stream/explore -> all activities (if plonesocial.network is installed)
    @@stream/tag/foobar -> all activities tagged #foobar
    '''

    implements(IPublishTraverse, IViewView, IBlocksTransformEnabled)

    index = ViewPageTemplateFile('templates/stream.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.tag = None
        # default to full stream
        self.explore = True

    def update(self):
        '''Mute plone.app.z3cform.kss.validation AttributeError'''
        pass

    def publishTraverse(self, request, name):
        ''' used for traversal via publisher, i.e. when using as a url '''
        if name == 'tag':
            stack = request.get('TraversalRequestNameStack')
            try:
                self.tag = stack.pop()
            except IndexError:
                # don't traceback on missing tag spec
                self.tag = None
        elif name == 'network':
            # @@stream/network enables 'following' filter
            self.explore = False
        return self

    @property
    def title(self):
        m_context = PLONESOCIAL.context(self.context)
        if m_context:
            return m_context.Title() + ' updates'
        elif self.explore:
            return _(u'Explore')
        else:
            return _(u'My network')
