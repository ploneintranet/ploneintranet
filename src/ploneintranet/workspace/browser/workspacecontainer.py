from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.memoize.view import memoize
from plone.tiles import Tile
from ploneintranet.workspace.browser.tiles.workspaces import my_workspaces
from ploneintranet.workspace.config import TEMPLATES_FOLDER
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

    def sort_options(self):
        options = [{'value': 'alphabet',
                    'content': 'Alphabetical'},
                   {'value': 'newest',
                    'content': 'Newest workspaces on top'},
                   # Not yet implemented
                   # {'value': 'activity',
                   #  'content': 'Most active workspaces on top'}
                   ]
        # put currently selected sort order at the beginning of the list
        if hasattr(self.request, "sort"):
            for o in options:
                if o['value'] == self.request.sort:
                    options.remove(o)
                    options.insert(0, o)
        return options

    @memoize
    def workspaces(self):
        ''' The list of my workspaces
        '''
        return my_workspaces(self.context, self.request)


class AddView(BrowserView):
    """ Add Form in a modal to create a new workspace """
    def workflows(self):
        return IMetroMap(self.context).get_available_metromap_workflows()

    def templates(self):
        portal = api.portal.get()
        pc = api.portal.get_tool('portal_catalog')
        brains = pc.searchResults(
            portal_type='ploneintranet.workspace.case',
            path='/'.join(portal.getPhysicalPath()) + '/' + TEMPLATES_FOLDER,
        )
        return brains


class WorkspaceTabsTile(Tile):

    index = ViewPageTemplateFile("templates/workspace-tabs-tile.pt")

    def render(self):
        return self.index()

    def __call__(self):
        return self.render()
