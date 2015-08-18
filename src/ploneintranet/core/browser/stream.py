# -*- coding: utf-8 -*-
from Products.Five import BrowserView
from plone.app.blocks.interfaces import IBlocksTransformEnabled
from plone.app.layout.globals.interfaces import IViewView
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet import api as piapi
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


class StreamView(BrowserView):

    '''Standalone view, providing
    - microblog input
    - activitystream rendering (via stream provider)

    @@stream -> either: all activities, or
             -> my network activities (if ploneintranet.network is installed)
    @@stream/explore -> all activities (if ploneintranet.network is installed)
    @@stream/tag/foobar -> all activities tagged #foobar
    '''

    implements(IPublishTraverse, IViewView, IBlocksTransformEnabled)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.tag = ''
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
        m_context = piapi.microblog.get_microblog_context(self.context)
        if m_context:
            return m_context.Title() + ' updates'
        elif self.explore:
            return _(u'Explore')
        else:
            return _(u'My network')
