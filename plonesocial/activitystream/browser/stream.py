from plone.tiles import Tile
from plonesocial.core.browser.stream import StreamBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class StreamTile(StreamBase, Tile):
    """Tile view similar to StreamView."""

    index = ViewPageTemplateFile("templates/stream_tile.pt")

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.tag = self.data.get('tag')
        self.explore = 'network' not in self.data
