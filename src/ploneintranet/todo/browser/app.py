# coding=utf-8
from collections import OrderedDict
from plone import api
from plone.memoize.view import memoize
from plone.memoize.view import memoize_contextless
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.layout.interfaces import IAppView
from ploneintranet.search.interfaces import ISiteSearch
from Products.Five import BrowserView
from zope.component import getUtility
from zope.interface import implementer


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

    _sort_mode_options = OrderedDict(
        [
            ('-modified', _('Newest first')),
            ('modified', _('Oldest first')),
            ('assignee', _('By assignee')),
            ('initiator', _('By initiator')),
            ('review_state', _('By task state')),
            ('priority', _('By priority')),
            ('sortable_title', _('Alphabetically')),
        ]
    )

    _state_mode_options = OrderedDict(
        [
            ('open', _('Open tickets')),
            ('closed', _('Closed tickets')),
            ('', _('All tickets')),
        ]
    )

    @property
    @memoize_contextless
    def userprofiles(self):
        ''' Return the userprofile container view
        '''
        portal = api.portal.get()
        return api.content.get_view(
            'view',
            portal.profiles,
            self.request,
        )

    @property
    @memoize
    def user(self):
        ''' Get the current user
        '''
        return self.userprofiles.user

    @property
    @memoize
    def add_task_url(self):
        ''' Convenience method to easily render the tabs in the template
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
            'origin',
        )
        options = []  # BBB
        return options

    @property
    @memoize
    def sort_mode_options(self):
        ''' The options for the sort mode
        '''
        options = self.options2items(
            self._sort_mode_options,
            'sort-mode',
            '-modified',
        )
        options = []  # BBB
        return options

    @property
    @memoize
    def state_mode_options(self):
        ''' The options for the sort mode
        '''
        options = self.options2items(
            self._state_mode_options,
            'state-mode',
            '',
        )
        options = []  # BBB
        return options

    @memoize
    def is_done(self, task):
        ''' Check if the task is done
        '''
        return api.content.get_state(obj=task) in self._done_states

    def search_tasks(self, filters={}, **params):
        """
        Search for specific content types
        """
        form = self.request.form
        keywords = form.get('SearchableText')
        filters['portal_type'] = 'todo'
        search_util = getUtility(ISiteSearch)
        response = search_util.query(
            keywords,
            filters,
            step=9999,
            **params
        )
        return response

    @property
    @memoize
    def personal_tasks(self):
        ''' Return the personal tasks
        '''
        if not self.user:
            return []
        path = '/'.join(self.user.getPhysicalPath())
        return [t.getObject() for t in self.search_tasks({'path': path})]

    @memoize
    def show_no_results(self):
        ''' Check if we should show the no result notice
        '''
        return not self.personal_tasks
