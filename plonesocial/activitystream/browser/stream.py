# coding=utf-8
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.tiles import Tile
from plonesocial.core.browser.stream import StreamBase
from zope.component import getMultiAdapter


class StreamTile(StreamBase, Tile):
    """Tile view similar to StreamView."""

    index = ViewPageTemplateFile("templates/stream_tile.pt")

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.tag = self.data.get('tag')
        self.explore = 'network' not in self.data

    @property
    def activity_providers(self):
        ''' Returtn the activity providers
        '''
        provider = getMultiAdapter(
            (self.context, self.request, self),
            name="plonesocial.core.stream_provider"
        )
        return provider.activity_providers
