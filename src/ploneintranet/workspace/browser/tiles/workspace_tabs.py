from plone.tiles import Tile
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize.view import memoize
from ...utils import parent_workspace


class WorkspaceTabsTile(Tile):

    index = ViewPageTemplateFile("templates/workspace-tabs-tile.pt")

    @memoize
    def workspace(self):
        # Attempt to acquire the current workspace
        return parent_workspace(self.context)

    def render(self):
        return self.index()

    def __call__(self):
        return self.render()
