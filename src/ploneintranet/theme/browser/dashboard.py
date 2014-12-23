from plone import api
from plone.tiles import Tile
from zope.publisher.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class Dashboard(BrowserView):
    """ A view to serve as a dashboard for homepage and/or users
    """


class NewsTile(Tile):

    index = ViewPageTemplateFile("templates/news-tile.pt")

    def render(self):
        return self.index()

    def __call__(self):
        return self.render()


class WorkspacesTile(Tile):

    index = ViewPageTemplateFile("templates/workspace-tile.pt")

    def workspaces(self):
        ''' The list of my workspaces
        '''
        pc = api.portal.get_tool('portal_catalog')
        return pc(
            portal_type="ploneintranet.workspace.workspacefolder",
            sort_on="modified",
            sort_order="reversed",
        )

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


class ActivityStreamTile(Tile):

    index = ViewPageTemplateFile("templates/activity-stream-tile.pt")

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
