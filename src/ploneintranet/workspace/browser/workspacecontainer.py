from Acquisition import aq_inner
from collections import defaultdict
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.memoize.view import memoize
from plone.tiles import Tile
from ploneintranet.core import ploneintranetCoreMessageFactory as _  # noqa
from ploneintranet.workspace.browser.tiles.workspaces import my_workspaces
from ploneintranet.workspace.config import TEMPLATES_FOLDER
from ploneintranet.workspace.workspacecontainer import IWorkspaceContainer
from zope.publisher.browser import BrowserView
from ploneintranet.workspace.interfaces import IMetroMap
from zope.schema.interfaces import IVocabularyFactory
from zope.component import getUtility

vocab = 'ploneintranet.workspace.vocabularies.Divisions'


class Workspaces(BrowserView):
    """ A view to serve as overview over workspaces """

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

    def get_selected_sort_option(self):
        ''' This will return the selected sort option

        The rules are:

        1. Check the request
        2. Check the registry
        3. Default to "alphabet"
        '''
        requested_sort = self.request.get('sort')
        if requested_sort:
            return requested_sort
        try:
            return api.portal.get_registry_record(
                'ploneintranet.workspace.my_workspace_sorting'
            )
        except api.exc.InvalidParameterError:
            # fallback if registry entry is not there
            return 'alphabet'

    def sort_options(self):
        options = [{'value': 'alphabet',
                    'content': _(u'Alphabetical')},
                   {'value': 'newest',
                    'content': _(u'Newest workspaces on top')},
                   # Not yet implemented
                   # {'value': 'activity',
                   #  'content': 'Most active workspaces on top'}
                   ]
        return options

    def grouping_options(self):
        options = [{'value': '',
                    'content': _(u'No grouping')},
                   {'value': 'division',
                    'content': _(u'Group by division')},
                   # Not yet implemented
                   # {'value': 'workspace_type',
                   #  'content': 'Group by workspace type'}
                   ]
        return options

    def workspace_types(self):
        options = [{'value': '',
                    'content': _(u'All workspace types')},
                   {'value': 'ploneintranet.workspace.workspacefolder',
                    'content': _(u'Generic workspaces')},
                   {'value': 'ploneintranet.workspace.case',
                    'content': _(u'Cases')},
                   ]
        return options

    def workspaces_by_division(self):
        ''' returns workspaces grouped by division
        '''
        workspaces = my_workspaces(self.context,
                                   self.request,
                                   include_activities=False)
        self.divisions = getUtility(IVocabularyFactory, vocab)(self.context)
        division_uids = [x.value for x in self.divisions]
        division_map = defaultdict(list)
        for workspace in workspaces:
            # Note: Already sorted as source list is sorted
            if workspace['uid'] in division_uids:
                division_map[workspace['uid']].append(workspace)
            else:
                division_map[workspace['division']].append(workspace)

        return division_map

    @memoize
    def workspaces(self):
        ''' The list of my workspaces
        '''
        return my_workspaces(self.context,
                             self.request,
                             include_activities=False)


class AddView(BrowserView):
    """ Add Form in a modal to create a new workspace """

    TEMPLATES_FOLDER = TEMPLATES_FOLDER
    types_with_policy = (
        'ploneintranet.workspace.workspacefolder',
    )

    def workflows(self):
        return IMetroMap(self.context).get_available_metromap_workflows()


class WorkspaceTabsTile(Tile):

    index = ViewPageTemplateFile("templates/workspace-tabs-tile.pt")

    def render(self):
        return self.index()

    def __call__(self):
        return self.render()
