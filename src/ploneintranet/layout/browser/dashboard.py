# coding=utf-8
from cgi import urlparse
from collections import OrderedDict
from collective.mustread.behaviors.maybe import IMaybeMustRead
from collective.mustread.interfaces import ITracker
from logging import getLogger
from plone import api
from plone.app.blocks.interfaces import IBlocksTransformEnabled
from plone.app.contenttypes.interfaces import IDocument
from plone.app.contenttypes.interfaces import IFile
from plone.app.contenttypes.interfaces import IImage
from plone.memoize import forever
from plone.memoize.view import memoize
from plone.memoize.view import memoize_contextless
from plone.tiles import Tile
from ploneintranet import api as pi_api
from ploneintranet.async.tasks import MarkRead
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.todo.utils import update_task_status
from ploneintranet.workspace.utils import parent_workspace
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from sqlalchemy.exc import OperationalError
from urllib import urlencode
from zope.component import getUtility
from zope.interface import implements
from zope.publisher.browser import BrowserView


logger = getLogger(__name__)


class Dashboard(BrowserView):

    """ A view to serve as a dashboard for homepage and/or users
    """
    _good_dashboards = [
        'activity',
        'custom',
        'task',
    ]

    implements(IBlocksTransformEnabled)

    @property
    @memoize
    def splashpage_uid(self):
        ''' Get the splashpage uid
        '''
        return api.portal.get_registry_record(
            'ploneintranet.layout.splashpage_uid',
            default='',
        )

    @property
    @memoize
    def show_splashpage(self):
        ''' Check if splashpage should be enabled
        '''
        if not api.portal.get_registry_record(
            'ploneintranet.layout.splashpage_enabled',
            default=False,
        ):
            return False
        user = self.user
        if not user:
            return False
        if getattr(user, 'splashpage_read', None) == self.splashpage_uid:
            return False
        return True

    @property
    @memoize
    def splashpage_content(self):
        ''' Check if splashpage should be enabled
        '''
        return api.portal.get_registry_record(
            'ploneintranet.layout.splashpage_content',
            default=''
        )

    def show_message(self, msg, type='success'):
        ''' Wrap show message to save some keystrokes
        '''
        return api.portal.show_message(msg, request=self.request, type=type)

    @property
    @memoize_contextless
    def user(self):
        ''' Return the current userprofile
        '''
        return pi_api.userprofile.get_current()

    @memoize_contextless
    def has_custom_dashboard(self):
        ''' Check if the functionality is allowed for the user
        '''
        return bool(self.user)

    @forever.memoize
    def tile_options(self, tile):
        ''' Return the name of the tile from the tile path
        '''
        qs = tile.partition('?')[-1]
        return urlparse.parse_qs(qs)

    @forever.memoize
    def get_tile_name(self, tile):
        ''' Return the name of the tile from the tile path
        '''
        options = self.tile_options(tile)
        return u' '.join(options.get('title', [tile]))

    @memoize
    def get_tile_display(self, tile):
        ''' Return the way the tile is displayed
        '''
        if not isinstance(tile, unicode):
            tile = tile.decode('utf8')
        return self.custom_tiles().get(tile, {}).get('display', 'span-1')

    @memoize
    def custom_tile_url(self, tile):
        ''' We need this to set the class parameter span-N
        '''
        if isinstance(tile, unicode):
            tile = tile.encode('utf8')
        url, qs = tile.partition('?')[::2]
        if not qs:
            return tile
        options = self.tile_options(tile)
        options.update(portletspan=self.get_tile_display(tile))
        return u'{url}?{qs}'.format(url=url, qs=urlencode(options, doseq=True))

    @memoize_contextless
    def available_custom_tiles(self):
        ''' This is a list of tiles that can be set in the user profile
        '''
        return api.portal.get_registry_record(
            'ploneintranet.layout.dashboard_custom_tiles',
            default=[
                './@@contacts_search.tile?title=Contacts',
                './@@news.tile?title=News',
                './@@my_documents.tile?title=My docs',
            ]
        )

    def custom_tiles(self):
        ''' This is an ordered dict of the tiles from the user profile
        plus the one available
        '''
        available = self.available_custom_tiles()
        user_defined = getattr(self.user, 'custom_tiles', OrderedDict())
        user_defined_keys = user_defined.keys()
        for tile in available:
            if tile not in user_defined_keys:
                user_defined.update({tile: {'display': 'span-1'}})
        return user_defined

    def activity_tiles(self):
        ''' This is a list of tiles taken
        '''
        return api.portal.get_registry_record(
            'ploneintranet.layout.dashboard_activity_tiles',
            default=[
                './@@contacts_search.tile',
                './@@news.tile',
                './@@my_documents.tile',
            ]
        )

    def task_tiles(self):
        ''' This is a list of tiles taken
        '''
        return api.portal.get_registry_record(
            'ploneintranet.layout.dashboard_task_tiles',
            default=[
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
        requested_dashboard = self.request.get('dashboard', '')
        user_dashboard = getattr(self.user, 'dashboard_default', '')

        # try to get the dashboard type to display:
        #  1. request has the priority
        #  2. then comes the user profile
        #  3. then the site default stored in the registry
        #  4. fall back on 'activity'
        dashboard = (
            requested_dashboard or
            user_dashboard or
            api.portal.get_registry_record(
                'ploneintranet.layout.dashboard_default',
                default='activity'
            )
        )
        # before returning the chosen dashboard check if
        # we have a requested value that should be persisted
        # on the user profile
        if (
            self.user and
            requested_dashboard in self._good_dashboards and
            requested_dashboard != user_dashboard
        ):
            self.user.dashboard_default = requested_dashboard

        return dashboard

    def maybe_mark_splashpage_as_read(self):
        ''' Check if we can mark this splash page as read
        If so add an attribute to the user
        '''
        splashpage_uid = self.request.form.get('splashpage_uid')
        if (
            not self.user or
            splashpage_uid != self.splashpage_uid
        ):
            # This is a debug feature to display again the splashpage
            if splashpage_uid == 'force':
                self.user.splashpage_read = ''
            return
        self.user.splashpage_read = splashpage_uid

    def __call__(self):
        ''' Do something before rendering the template
        '''
        self.maybe_mark_splashpage_as_read()
        return super(Dashboard, self).__call__()


class NewsTile(Tile):

    index = ViewPageTemplateFile("templates/news-tile.pt")

    @property
    @memoize
    def just_read_uids(self):
        ''' Try hard to get a just_read_uids parameter from the request
        and makle a list of it

        Append to the list also
        '''

        just_read_uids = self.request.get('just_read_uids')
        if not just_read_uids:
            just_read_uids = []
        elif isinstance(just_read_uids, basestring):
            just_read_uids = [just_read_uids]
        elif not isinstance(just_read_uids, list):
            just_read_uids = list(just_read_uids)

        hit_uid = self.request.form.get('hit_uid')

        if hit_uid and isinstance(hit_uid, basestring):
            item = api.content.get(UID=hit_uid)
            # async write on-disk state
            MarkRead(item, self.request)()
            # sync update in-memory state
            just_read_uids.append(hit_uid)

        return just_read_uids

    @property
    @memoize_contextless
    def cropText(self):
        ''' Reuse the homonynous function from the plone view
        '''
        plone_view = api.content.get_view(
            'plone',
            self.context,
            self.request,
        )
        return plone_view.cropText

    def get_cropped_description(self, brain):
        ''' We want the description to be cropped
        '''
        length = 120 - len(brain.Title or'')
        return self.cropText(brain.Description, length)

    def get_img_style(self, item, scale='mini'):
        ''' Return the style for the image tag
        '''
        if not item.get('has_thumbs'):
            return None
        url = item['url']
        return 'background-image: url({url}/@@images/image/{scale})'.format(
            scale=scale,
            url=url,
        )

    @property
    @memoize
    def batch_size(self):
        ''' Check if we should batch the news_item
        '''
        if self.request.form.get('portlet-news-state-expanded') == 'on':
            return 0
        return 4

    @memoize
    def news_items(self):
        tracker = getUtility(ITracker)
        try:
            read_uids = set(tracker.uids_read() or [])
        except OperationalError:  # sqlite not supported in robot tests
            read_uids = set()
            logger.error('Cannot query read tracker, will assume news unread.')
        # supplement async tracker with sync hidden state propagation
        read_uids.update(self.just_read_uids)

        pc = api.portal.get_tool('portal_catalog')
        query = dict(portal_type='News Item',
                     sort_on='effective',
                     sort_order='reverse'
                     )
        if api.portal.get_registry_record(
           'ploneintranet.layout.filter_news_by_published_state') is True:
            query.update(review_state='published')
        results = pc(query)

        items = [
            {'title': item.Title,
             'description': self.get_cropped_description(item),
             'url': item.getURL(),
             'uid': item.UID,
             'has_thumbs': item.has_thumbs,
             'item': item}
            for item in results
            if item.UID not in read_uids
        ]
        for item in items:
            obj = item['item'].getObject()
            item['must_read'] = IMaybeMustRead(obj).must_read
        # sort must-read, then on effective
        items.sort(key=lambda x: x['must_read'], reverse=True)

        # BBB: implement a proper batching with autoload
        batch_size = self.batch_size
        if not batch_size:
            return items
        return items[:batch_size]

    def can_expand(self):
        return len(self.news_items()) > self.min_num()

    @memoize
    def min_num(self):
        return api.portal.get_registry_record(
            'ploneintranet.layout.min_news_items',
            default=3,
        )

    @memoize
    def max_num(self):
        return api.portal.get_registry_record(
            'ploneintranet.layout.max_news_items',
            default=10,
        )


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
        portal = api.portal.get()
        self.task_app = "{}/apps/todo/@@my-tasks".format(
            portal.absolute_url())

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
            # No workspace == personal task
            if workspace is None:
                personal_id = '_personal_tasks'
                if personal_id not in self.grouped_tasks:

                    self.grouped_tasks[personal_id] = {
                        'title': _(u'Personal tasks'),
                        'url': self.task_app,
                        'tasks': []
                    }
                self.grouped_tasks[personal_id]['tasks'].append(task)
            else:
                if workspace.id not in self.grouped_tasks:
                    self.grouped_tasks[workspace.id] = {
                        'title': workspace.title,
                        'url': workspace.absolute_url(),
                        'tasks': [],
                    }
                self.grouped_tasks[workspace.id]['tasks'].append(task)
        return self.render()


class EditDashboard(Dashboard):
    ''' Edit the dashboard custom tiles
    '''
    def reset_custom_tiles(self):
        ''' Reset the custom_tile storage
        '''
        self.user.custom_tiles = OrderedDict()

    def is_resizable(self, tile):
        ''' The noresize=1 query string parameter disable the size selction
        '''
        if 'noresize' in self.tile_options(tile):
            return False
        return True

    def allow_fullpage(self, tile):
        ''' The noresize=1 query string parameter disable the size selction
        '''
        if 'nofullpage' in self.tile_options(tile):
            return False
        return True

    def maybe_update_tiles(self):
        ''' Update the custom tiles if needed
        '''
        if not self.has_custom_dashboard():
            self.show_message(_('Function not allowed'), type='error')
            return

        if self.request.form.get('restore', False):
            self.reset_custom_tiles()
            return self.show_message(_('Default dashboard restored'))

        requested_tiles = self.request.form.get('tiles_order') or []
        available = self.available_custom_tiles()
        tiles = OrderedDict()
        for tile in requested_tiles:
            tile_decoded = tile.decode('utf8')
            if tile_decoded in available:
                tiles[tile_decoded] = {
                    'display': self.request.get('display-%s' % tile, 'span-1'),
                }

        if tiles != self.custom_tiles():
            self.user.custom_tiles = tiles
            return self.show_message(_('Dashboard order changed'))

        return self.show_message(
            _('Dashboard order unchanged'),
            type='warning'
        )

    def __call__(self):
        ''' Update tiles if needed
        '''
        if self.request.method == 'POST':
            self.maybe_update_tiles()
            return self.request.response.redirect(
                self.context.absolute_url() + '/dashboard.html'
            )
        return super(EditDashboard, self).__call__()


class MyDocumentsTile(Tile):

    def my_documents(self):
        """
        Return the X most recently modified documents which I have the
        permission to view.
        """
        catalog = api.portal.get_tool('portal_catalog')
        try:
            max_num = api.portal.get_registry_record(
                'ploneintranet.layout.max_library_items'
            )
        except api.exc.InvalidParameterError:
            # fallback if registry entry is not there
            max_num = 20
        recently_modified_items = catalog.searchResults(
            object_provides=[
                IDocument.__identifier__,
                IFile.__identifier__,
                IImage.__identifier__,
            ],
            sort_on='modified',
            sort_limit=max_num,
            sort_order='descending',
        )
        return recently_modified_items
