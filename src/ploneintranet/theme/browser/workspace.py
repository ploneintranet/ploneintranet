from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize.view import memoize
from plone.tiles import Tile
from ploneintranet.workspace.browser.tiles.workspaces import my_workspaces
from zope.publisher.browser import BrowserView


class Workspaces(BrowserView):

    """ A view to serve as overview over workspaces
    """

    """ The tiles below are dummy tiles.
         Please do NOT implement real tiles here, put them in another package.
         We want to keep the theme simple and devoid of business logic
    """
    @memoize
    def workspaces(self):
        ''' The list of my workspaces
        '''
        return my_workspaces(self.context)


class AddView(BrowserView):
    """ Add Form in a modal to create a new workspace """


class WorkspaceTabsTile(Tile):

    index = ViewPageTemplateFile("templates/workspace-tabs-tile.pt")

    def render(self):
        return self.index()

    def __call__(self):
        return self.render()
