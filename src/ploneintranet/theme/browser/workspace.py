from plone import api
from plone.tiles import Tile
from zope.publisher.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class WorkspaceTabsTile(Tile):

    index = ViewPageTemplateFile("templates/workspace-tabs-tile.pt")

    def render(self):
        return self.index()

    def __call__(self):
        return self.render()
