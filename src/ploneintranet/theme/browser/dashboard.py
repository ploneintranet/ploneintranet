from plone import api
from plone.memoize.view import memoize
from plone.tiles import Tile
from zope.publisher.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class Dashboard(BrowserView):

    """ A view to serve as a dashboard for homepage and/or users
    """

    """ The tiles below are dummy tiles.
         Please do NOT implement "real" tiles here, put them in another package.
         We want to keep the theme simple and devoid of business logic
    """


class NewsTile(Tile):

    index = ViewPageTemplateFile("templates/news-tile.pt")

    def render(self):
        return self.index()

    def __call__(self):
        return self.render()


class TasksTile(Tile):

    index = ViewPageTemplateFile("templates/tasks-tile.pt")

    def render(self):
        return self.index()

    def __call__(self):
        return self.render()


class NewPostBoxTile(Tile):

    index = ViewPageTemplateFile("templates/new-post-box-tile.pt")

    def render(self):
        return self.index()

    def __call__(self):
        return self.render()
