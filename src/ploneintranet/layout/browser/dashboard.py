from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.app.blocks.interfaces import IBlocksTransformEnabled
from plone.tiles import Tile
from ploneintranet.layout.browser import google_auth
from ploneintranet.workspace.utils import parent_workspace
from ploneintranet.todo.utils import update_task_status
from zope.interface import implements
from zope.publisher.browser import BrowserView

import logging
logger = logging.getLogger(__name__)


class Dashboard(BrowserView):

    """ A view to serve as a dashboard for homepage and/or users
    """

    implements(IBlocksTransformEnabled)


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
                  review_state='published',
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


class DriveRecentTile(Tile):

    index = ViewPageTemplateFile("templates/recent-docs.pt")

    def render(self):
        return self.index()

    def have_credentials(self):
        try:
            return google_auth.get_pi_users_credentials()
        except KeyError:
            return False

    def auth_url(self):
        user = api.user.get_current()
        return self.request.response.redirect(
            google_auth.get_authorization_url(
                user.id,
                1))

    def docs(self):
        credentials = self.have_credentials()
        try:
            service = google_auth.build_service(credentials)
            resp = service.files().list().execute()
        except:
            logger.exception('Error getting docs from drive')
            google_auth.remove_pi_users_credentials()
            return []
        return resp['items']
