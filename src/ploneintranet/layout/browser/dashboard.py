from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.app.blocks.interfaces import IBlocksTransformEnabled
from plone.tiles import Tile
from ploneintranet.workspace.utils import parent_workspace
from zope.interface import implements
from zope.publisher.browser import BrowserView


class Dashboard(BrowserView):

    """ A view to serve as a dashboard for homepage and/or users
    """

    implements(IBlocksTransformEnabled)


# The tiles below are dummy tiles.
# Please do NOT implement "real" tiles here, put them in another package
# We want to keep the theme simple and devoid of business logic
# class NewsTile(Tile):

#     index = ViewPageTemplateFile("templates/news-tile.pt")

#     def render(self):
#         return self.index()

#     def __call__(self):
#         return self.render()


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
