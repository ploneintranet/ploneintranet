# coding=utf-8
from collections import defaultdict
from collections import OrderedDict
from itertools import imap
from logging import getLogger
from plone import api
from plone.memoize import forever
from plone.memoize.view import memoize
from plone.memoize.view import memoize_contextless
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.layout.interfaces import IAppView
from ploneintranet.search.interfaces import ISiteSearch
from ploneintranet.todo.vocabularies import todo_priority
from ploneintranet.workspace.utils import parent_workspace
from Products.Five import BrowserView
from scorched.dates import solr_date
from urllib import urlencode
from zope.component import getUtility
from zope.interface import implementer


logger = getLogger(__name__)


@implementer(IAppView)
class View(BrowserView):
    ''' The view for this app
    '''
    app_name = 'todo'

    _done_states = (
        'done',
    )

    _navigation_tabs = OrderedDict(
        [
            ('@@app-todo', _('All tasks')),
            ('@@my-tasks', _('My tasks')),
            ('@@personal-tasks', _('Personal tasks')),
        ]
    )

    _browse_mode_default = 'origin'
    _browse_mode_options = OrderedDict(
        [
            ('origin', _('Group by origin')),
            ('origin_and_milestone', _('Group by origin and milestone')),
            ('assignee', _('Group by assignee')),
            ('initiator', _('Group by initiator')),
            ('task_state', _('Group by task state')),
            ('priority', _('Group by priority')),
            ('', _('No grouping')),
        ]
    )

    _sort_mode_default = '-modified'
    _sort_mode_options = OrderedDict(
        [
            ('-modified', _('Newest first')),
            ('modified', _('Oldest first')),
            ('assignee', _('By assignee')),
            ('initiator', _('By initiator')),
            ('review_state', _('By task state')),
            ('-priority', _('By priority')),
            ('sortable_title', _('Alphabetically')),
        ]
    )

    _state_mode_default = ''
    _state_mode_options = OrderedDict(
        [
            ('open', _('Open tickets')),
            ('done', _('Closed tickets')),
            ('', _('All tickets')),
        ]
    )

    _search_tasks_limit = 100

    show_initiators = True
    show_assignes = True

    @property
    @memoize_contextless
    def portal(self):
        ''' Return the userprofile container view
        '''
        return api.portal.get()

    @property
    @memoize_contextless
    def userprofiles(self):
        ''' Return the userprofile container view
        '''
        return api.content.get_view(
            'view',
            self.portal.profiles,
            self.request,
        )

    @property
    def results_view(self):
        ''' Return a view that renders the search results
        '''
        return api.content.get_view(
            '{}-search-results'.format(self.__name__),
            self.context,
            self.request,
        )

    def reset_url(self):
        ''' Return the url without -search-results
        '''
        name = self.__name__
        if name.endswith('-search-results'):
            name = name.rsplit('-', 2)[0]
        return name

    @memoize_contextless
    def get_prio_class(self, priority):
        ''' Return a class to set the priority market
        '''
        classes = {
            0: 'priority-low',
            1: 'priority-medium',
            2: 'priority-high',
        }
        return classes.get(priority, '')

    @property
    @memoize
    def allusers_json_url(self):
        ''' Return @@allusers.json in the proper context
        '''
        return '{}/@@allusers.json'.format(
            self.portal.profiles.absolute_url()
        )

    def get_data_pat_autosuggest(self):
        ''' Return the data-pat-autosuggest for a fieldname
        '''
        options = [
            'ajax-data-type: json',
            'maximum-selection-size: 1',
            'selection-classes: {}',
            'ajax-url: {}'.format(self.allusers_json_url),
            'allow-new-words: false',
        ]
        return '; '.join(options)

    @property
    @memoize_contextless
    def workspace_container(self):
        ''' Return the userprofile container view
        '''
        return self.portal.workspaces

    @property
    @memoize
    def user(self):
        ''' Get the current user
        '''
        return self.userprofiles.user

    @property
    @memoize
    def add_task_url(self):
        ''' The URL for adding a personal tasks
        '''
        user = self.user
        if not user:
            return
        return '{}/@@add_task'.format(user.absolute_url())

    @property
    @memoize
    def navigation_tabs(self):
        ''' Convenience method to easily render the tabs in the template
        '''
        base_url = self.context.absolute_url()
        items = [
            {
                'url': '{base_url}/{view}'.format(
                    base_url=base_url,
                    view=view,
                ),
                'label': label,
                'klass': 'current' if self.__name__ == view.lstrip('@') else ''
            } for view, label in self._navigation_tabs.iteritems()
        ]
        return items

    def options2items(self, options, fieldname, default=''):
        ''' Make items that will be rendered in a page template
        '''
        selected = self.request.form.get(fieldname, default)
        return [
            {
                'value': value,
                'label': label,
                'selected': selected == value and 'selected' or None,
            }
            for value, label in options.iteritems()
        ]

    @property
    @memoize
    def browse_mode_options(self):
        ''' The options for the browsing mode
        '''
        options = self.options2items(
            self._browse_mode_options,
            'browse-mode',
            self._browse_mode_default,
        )
        return options

    @property
    @memoize
    def browse_mode(self):
        return self.request.form.get(
            'browse-mode',
            self._browse_mode_default,
        )

    @property
    @memoize
    def sort_mode_options(self):
        ''' The options for the sort mode
        '''
        options = self.options2items(
            self._sort_mode_options,
            'sort-mode',
            self._sort_mode_default,
        )
        return options

    @property
    @memoize
    def state_mode_options(self):
        ''' The options for the sort mode
        '''
        options = self.options2items(
            self._state_mode_options,
            'state-mode',
            self._state_mode_default,
        )
        return options

    @memoize
    def is_done(self, task):
        ''' Check if the task is done
        '''
        return api.content.get_state(obj=task) in self._done_states

    def set_filters(self, filters):
        ''' Customizable filters for the view
        '''
        form = self.request.form
        filters['portal_type'] = 'todo'
        filters['path'] = self.searched_paths
        state_mode = form.get('state-mode', self._state_mode_default)
        if state_mode:
            filters['review_state'] = state_mode
        start = form.get('start', None)
        end = form.get('end', None)
        if start and end:
            filters['due__range'] = (solr_date(start), solr_date(end))
        elif start:
            filters['due__ge'] = solr_date(start)
        elif end:
            filters['due__le'] = solr_date(end)
        for key in (
            'assignee',
            'initiator',
        ):
            value = form.get(key, None)
            if value:
                filters[key] = value

    def search_tasks(self, filters={}, **params):
        """
        Search for specific content types
        """
        filters = filters.copy()
        form = self.request.form
        keywords = form.get('SearchableText')
        self.set_filters(filters)
        search_util = getUtility(ISiteSearch)
        _params = {
            'sort': form.get('sort-mode', self._sort_mode_default),
            'step': self._search_tasks_limit,
        }
        _params.update(params)
        response = search_util.query(
            keywords,
            filters,
            **_params
        )
        return response

    @memoize
    def show_lenght_warning(self):
        ''' The search results are limited. Show a warning
        the suggests to play with filters
        '''
        return len(self.tasks) >= self._search_tasks_limit

    @property
    @memoize
    def searched_paths(self):
        ''' Return the tasks inside workspaces
        '''
        paths = [
            '/'.join(obj.getPhysicalPath())
            for obj in (
                self.workspace_container,
                self.portal.profiles,
            )
        ]
        return paths

    @property
    @memoize
    def tasks(self):
        ''' Return the tasks inside workspaces
        '''
        if not self.searched_paths:
            return []
        return filter(None, (t.getObject() for t in self.search_tasks()))

    @property
    @memoize
    def tasks_by_workspace(self):
        ''' Return the tasks inside workspaces grouped by workspace
        '''
        tasks = self.tasks
        tasks_by_workspace = defaultdict(list)
        for task in tasks:
            workspace = parent_workspace(task)
            tasks_by_workspace[workspace].append(task)
        return tasks_by_workspace

    def get_key_maker(self):
        ''' Return a function that will generate a key
        according to the selected browsing mode
        The key can be the parent workspace, an attribute value,
        the review state or whatever.

        As a fallback we return a function that returns None.
        '''
        browse_mode = self.browse_mode
        if browse_mode in ('origin', 'assigned', 'initiated'):
            return parent_workspace
        if browse_mode == 'origin_and_milestone':
            return lambda task: (parent_workspace(task), task.milestone)
        if browse_mode == 'task_state':
            return api.content.get_state
        if browse_mode in (
            'assignee',
            'initiator',
            'priority',
        ):
            return lambda task: getattr(task, browse_mode, None)
        return lambda task: None

    def _origin_key_beautifier(self, key):
        ''' We expect key to be either a workspace or None
        '''
        if not key:
            return {
                'icon': 'icon-user',
                'klass': 'personal',
                'key': key,
                'title': _('Personal tasks'),
                'sorting_key': ' ',
            }
        else:
            return {
                'key': key,
                'title': key.title,
                'url': key.absolute_url(),
            }

    def _origin_and_milestone_key_beautifier(self, key):
        ''' We expect key to be a tuple containing a workspace and a milestone
        '''
        ws, milestone = key
        if not ws:
            return {
                'icon': 'icon-user',
                'klass': 'personal',
                'key': key,
                'title': _('Personal tasks'),
                'sorting_key': ' ',
            }
        if milestone:
            title = u' - '.join((ws.title, milestone))
            add_params = urlencode({'milestone': milestone})
        else:
            title = ws.title
            add_params = ''
        return {
            'key': key,
            'title': title,
            'url': ws.absolute_url(),
            'add_params': add_params,
        }

    def _userid_key_beautifier(self, key):
        ''' We expect key to be a userid
        '''
        fullname = self.userprofiles.get_fullname_for(key)
        return {
            'title': fullname or _('None'),
            'key': key,
            'sorting_key': fullname or ' '
        }

    def _priority_key_beautifier(self, key):
        ''' We expect key to be a priority level
        '''
        try:
            title = todo_priority.getTerm(key).title
        except:
            logger.warning(
                'Cannot get priority label for value: %r',
                key,
            )
            title = key
        return {
            'title': title,
            'key': key,
            'sorting_key': str(-key + 50),
        }

    def get_key_beautifier(self):
        '''Return a function that will transform a key in to something
        that can be rendered in the template
        '''
        browse_mode = self.browse_mode
        if browse_mode in ('origin', 'assigned', 'initiated'):
            return self._origin_key_beautifier
        if browse_mode == 'origin_and_milestone':
            return self._origin_and_milestone_key_beautifier
        if browse_mode in ('assignee', 'initiator'):
            return self._userid_key_beautifier
        if browse_mode == 'priority':
            return self._priority_key_beautifier
        return lambda key: {'title': key, 'key': key}

    @property
    @memoize
    def tasks_by_group(self):
        ''' Return the tasks grouped according to the browse mode

        The beautifier function is a dict like object with a key, a title
        and other optional key/value pairs that may be used in the template
        '''
        key_maker = self.get_key_maker()
        tasks_by_group = defaultdict(list)
        for task in self.tasks:
            key = key_maker(task)
            tasks_by_group[key].append(task)
        return tasks_by_group

    @property
    @memoize
    def beautified_keys(self):
        ''' Return the sorted keys for our browse mode
        The keys need to be beautified in order to be rendered in the template.
        '''
        key_beautifier = self.get_key_beautifier()
        groups = imap(key_beautifier, self.tasks_by_group)
        return sorted(
            groups,
            key=lambda g: g.get('sorting_key') or g['title'],
        )

    @memoize
    def show_no_results(self):
        ''' Check if we should show the no result notice
        '''
        return not self.tasks

    def show_reset_button(self):
        ''' Show the reset button if we have something in the query string
        '''
        keys = self.request.form.keys()
        return keys and keys != ['_']


class MyTasksView(View):
    ''' The tasks assigned to me
    '''

    show_assignes = False

    @property
    @forever.memoize
    def _browse_mode_options(self):
        ''' Remove the assignee option because it is always the current user
        '''
        options = super(MyTasksView, self)._browse_mode_options.copy()
        options.pop('assignee')
        return options

    def set_filters(self, filters={}, **params):
        ''' Filter by assignee with my userid
        '''
        super(MyTasksView, self).set_filters(filters)
        if not self.user:
            return
        filters['assignee'] = self.user.username

    @property
    @memoize
    def searched_paths(self):
        ''' Return the tasks inside workspaces
        '''
        if self.user:
            return '/'.join(self.user.getPhysicalPath())
        return ''


class PersonalTasksView(View):
    ''' My personal tasks
    '''
    _browse_mode_default = ''
    _browse_mode_options = OrderedDict(
        [
            ('', _('All personal tickets')),
            ('assigned', _('Personal tickets assigned to me by others')),
            ('initiated', _('Personal tickets that I assigned to others')),
        ]
    )

    show_initiators = False
    show_assignes = False

    def set_filters(self, filters={}, **params):
        ''' Filter by assignee with my userid
        '''
        super(PersonalTasksView, self).set_filters(filters)
        browse_mode = self.browse_mode
        if browse_mode == 'assigned':
            filters['assignee'] = self.user.username
        elif browse_mode == 'initiated':
            filters['initiator'] = self.user.username

    def get_key_maker(self):
        ''' Personal tasks are not grouped
        '''
        return lambda task: None

    def get_key_beautifier(self):
        '''Return a function that will transform a key in to something
        that can be rendered in the template
        '''
        return self._origin_key_beautifier

    @property
    @memoize
    def searched_paths(self):
        ''' Return the tasks inside workspaces
        '''
        if not self.user and self.browse_mode:
            return []
        return '/'.join(self.portal.profiles.getPhysicalPath())
