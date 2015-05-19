import urllib
from plone.app.blocks.interfaces import IBlocksTransformEnabled
from plone.tiles import Tile
from plone import api
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements
from zope.publisher.browser import BrowserView


class Dashboard(BrowserView):

    """ A view to serve as a dashboard for homepage and/or users
    """

    """ The tiles below are dummy tiles.
         Please do NOT implement "real" tiles here, put them in another package
         We want to keep the theme simple and devoid of business logic
    """
    implements(IBlocksTransformEnabled)

    def __call__(self):
        portal = api.portal.get()
        if api.user.is_anonymous():
            return self.request.response.redirect(
                '%s/login?%s' % (
                    portal.absolute_url(),
                    urllib.urlencode(
                        {
                            'came_from': '%s/%s' % (
                                self.context.absolute_url(),
                                '/dashboard.html'
                            )
                        }
                    )
                )
            )
        return self.index()


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
