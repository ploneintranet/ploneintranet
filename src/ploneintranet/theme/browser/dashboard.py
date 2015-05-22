from plone.app.blocks.interfaces import IBlocksTransformEnabled
from plone.tiles import Tile
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements
from zope.publisher.browser import BrowserView


class Dashboard(BrowserView):

    """ A view to serve as a dashboard for homepage and/or users
    """

    implements(IBlocksTransformEnabled)


# The tiles below are dummy tiles.
# Please do NOT implement "real" tiles here, put them in another package
# We want to keep the theme simple and devoid of business logic
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
