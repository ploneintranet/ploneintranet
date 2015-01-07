from plone import api
from plone.tiles import Tile
from zope.publisher.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class Sidebar(BrowserView):

    """ A view to serve as a sidebar for workspaces
    """

    """ The tiles below are dummy tiles.
         Please do NOT implement "real" tiles here, put them in another package.
         We want to keep the theme simple and devoid of business logic
    """


class Tile(Tile):

    index = ViewPageTemplateFile("templates/sidebar-tile.pt")

    def render(self):
        return self.index()

    def __call__(self):
        return self.render()
