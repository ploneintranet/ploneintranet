# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.tiles import Tile
from plonesocial.core.browser.stream import StreamBase


class NewPostBoxTile(Tile, StreamBase):

    index = ViewPageTemplateFile('templates/new-post-box-tile.pt')

    def render(self):
        return self.index()

    def __call__(self):
        if self.request.form:
            view = api.content.get_view(
                'stream',
                self.context,
                self.request,
            )
            view()
        return self.render()
