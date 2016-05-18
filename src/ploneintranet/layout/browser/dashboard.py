# coding=utf-8
from logging import getLogger
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.app.blocks.interfaces import IBlocksTransformEnabled
from plone.app.contenttypes.interfaces import IDocument
from plone.app.contenttypes.interfaces import IFile
from plone.app.contenttypes.interfaces import IImage
from plone.tiles import Tile
from ploneintranet.layout.utils import get_record_from_registry
from ploneintranet.workspace.utils import parent_workspace
from ploneintranet.todo.utils import update_task_status
from zope.interface import implements
from zope.publisher.browser import BrowserView


logger = getLogger(__name__)


class Dashboard(BrowserView):

    """ A view to serve as a dashboard for homepage and/or users
    """

    implements(IBlocksTransformEnabled)

    def activity_tiles(self):
        ''' This is a list of tiles taken
        '''
        return get_record_from_registry(
            'ploneintranet.layout.dashboard_activity_tiles',
            fallback=[
                './@@contacts_search.tile',
                './@@news.tile',
                './@@my_documents.tile',
            ]
        )

    def task_tiles(self):
        ''' This is a list of tiles taken
        '''
        return get_record_from_registry(
            'ploneintranet.layout.dashboard_task_tiles',
            fallback=[
                './@@news.tile',
                './@@my_documents.tile',
                './@@workspaces.tile?workspace_type=ploneintranet.workspace.workspacefolder',  # noqa
                './@@workspaces.tile?workspace_type=ploneintranet.workspace.case',  # noqa
                './@@events.tile',
                './@@tasks.tile',
            ]
        )

    def default_dashboard(self):
        ''' Returns the dashboard name which is set as default in the registry
        '''
        registry_default = get_record_from_registry(
            'ploneintranet.layout.dashboard_default',
            fallback='activity')
        return self.request.get('dashboard', registry_default)


class NewsTile(Tile):

    index = ViewPageTemplateFile("templates/news-tile.pt")

    def render(self):
        return self.index()

    def __call__(self):
        """
        Display a list of News items ordered by date.
        """
        pc = api.portal.get_tool('portal_catalog')
        news = pc(portal_type='News Item',
                  sort_on='effective',
                  sort_order='reverse')
        self.news_items = []
        for item in news[:3]:
            self.news_items.append({
                'title': item.Title,
                'description': item.Description,
                'url': item.getURL(),
                'has_thumbs': item.has_thumbs
            })
        return self.render()


class TasksTile(Tile):

    index = ViewPageTemplateFile("templates/tasks-tile.pt")

    def render(self):
        return self.index()

    def __call__(self):
        """Display a list of Todo items in the Open workflow state, grouped by
        Workspace and ordered by Due date.
        {'workspace1': {'title': 'WS1', 'url': '...', 'tasks':[<brain>, ...]}}
        """
        pc = api.portal.get_tool('portal_catalog')
        me = api.user.get_current().getId()
        form = self.request.form

        if self.request.method == 'POST' and form:
            return update_task_status(self, return_status_message=True)

        tasks = pc(portal_type='todo',
                   review_state='open',
                   assignee=me,
                   sort_on='due')
        self.grouped_tasks = {}
        for task in tasks:
            obj = task.getObject()
            workspace = parent_workspace(obj)
            if workspace.id not in self.grouped_tasks:
                self.grouped_tasks[workspace.id] = {
                    'title': workspace.title,
                    'url': workspace.absolute_url(),
                    'tasks': [task],
                }
            else:
                self.grouped_tasks[workspace.id]['tasks'].append(task)
        return self.render()


class MyDocumentsTile(Tile):

    def my_documents(self):
        """
        Return the 10 most recently modified documents which I have the
        permission to view.
        """
        catalog = api.portal.get_tool('portal_catalog')

        recently_modified_items = catalog.searchResults(
            object_provides=[
                IDocument.__identifier__,
                IFile.__identifier__,
                IImage.__identifier__,
            ],
            sort_on='modified',
            sort_limit=10,
            sort_order='descending',
        )
        return recently_modified_items
