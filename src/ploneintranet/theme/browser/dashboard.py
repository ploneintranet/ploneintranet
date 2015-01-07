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


class WorkspacesTile(Tile):

    index = ViewPageTemplateFile("templates/workspace-tile.pt")

    def get_workspace_activities(self, brain, limit=1):
        ''' Return the workspace activities sorted by reverse chronological
        order

        Regarding the time value:
         - the datetime value contains the time in international format
           (machine readable)
         - the title value contains the absolute date and time of the post
        '''
        # BBB: this is a mock!!!!
        return [
            {
                'subject': 'Charlotte Holzer',
                'verb': 'published',
                'object': 'Proposal draft V1.0 # This is a mock!!!',
                'time': {
                    'datetime': '2008-02-14',
                    'title': '5 October 2015, 18:43',
                }
            }
        ][:limit]

    @memoize
    def workspaces(self):
        ''' The list of my workspaces
        '''
        pc = api.portal.get_tool('portal_catalog')
        brains = pc(
            portal_type="ploneintranet.workspace.workspacefolder",
            sort_on="modified",
            sort_order="reversed",
        )
        workspaces = [
            {
                'title': brain.Title,
                'description': brain.Description,
                'url': brain.getURL(),
                'activities': self.get_workspace_activities(brain),
            } for brain in brains
        ]
        return workspaces

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
