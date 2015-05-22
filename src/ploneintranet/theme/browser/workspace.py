from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.memoize.view import memoize
from plone.tiles import Tile
from ploneintranet.workspace.browser.tiles.workspaces import my_workspaces
from ploneintranet.workspace.workspacecontainer import IWorkspaceContainer
from zope.publisher.browser import BrowserView
from ploneintranet.workspace.interfaces import IMetroMap


class Workspaces(BrowserView):

    """ A view to serve as overview over workspaces
    """

    """ The tiles below are dummy tiles.
         Please do NOT implement real tiles here, put them in another package.
         We want to keep the theme simple and devoid of business logic
    """

    def __call__(self):
        """Render the default template"""
        context = aq_inner(self.context)
        if IWorkspaceContainer.providedBy(context):
            self.target = context
        else:
            # hardcoded at the moment to fetch a folder called 'workspaces'
            self.target = getattr(context, 'workspaces')
        self.can_add = api.user.has_permission(
            'Add portal content',
            obj=self.target
        )
        return super(Workspaces, self).__call__()

    @memoize
    def workspaces(self):
        ''' The list of my workspaces
        '''
        return my_workspaces(self.context)


class AddView(BrowserView):
    """ Add Form in a modal to create a new workspace """
    def workflows(self):
        return IMetroMap(self.context).get_available_metromap_workflows()


class WorkspaceTabsTile(Tile):

    index = ViewPageTemplateFile("templates/workspace-tabs-tile.pt")

    def render(self):
        return self.index()

    def __call__(self):
        return self.render()
