# coding=utf-8
from ..interfaces import ITodoUtility
from collections import OrderedDict
from itertools import imap
from json import dumps
from logging import getLogger
from plone import api
from plone.app.blocks.interfaces import IBlocksTransformEnabled
from plone.memoize.view import memoize
from ploneintranet import api as pi_api
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.layout.browser.workflow import WorkflowMenu
from ploneintranet.layout.interfaces import IDiazoAppTemplate
from ploneintranet.workspace.basecontent.baseviews import ContentView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility
from zope.interface import implementer


log = getLogger(__name__)


class BaseView(ContentView):

    def __init__(self, context, request):
        super(BaseView, self).__init__(context, request)
        self.util = getUtility(ITodoUtility)
        self.current_user_id = api.user.get_current().getId()
        self.content_uid = api.content.get_uuid(self.context)


@implementer(IBlocksTransformEnabled, IDiazoAppTemplate)
class TodoView(BaseView):

    @property
    @memoize
    def logical_parent(self):
        ''' Tries to find the best logical parent for this object.
        It may be a workspace or a userprofile if the todo is a personal task
        '''
        return self.workspace or self.context.aq_parent

    @property
    def sidebar_target(self):
        ''' When injecting the form we may want to reload some sidebar parts
        '''
        return 'todo-{UID}'.format(
            UID=self.context.UID()
        )

    @memoize
    def is_done(self):
        ''' Check if this task is done
        '''
        return api.content.get_view(
            'workflow_menu',
            self.context,
            self.request,
        ).is_done()

    def update(self):
        """ """
        if ('task_action' in self.request and
                not self.request.get('form.submitted')):
            task_action = self.request.get('task_action')
            if task_action == 'close':
                api.content.transition(
                    obj=self.context,
                    transition='finish'
                )
            elif task_action == 'reopen':
                self.context.reopen()
            api.portal.show_message(_(
                'Changes applied'), request=self.request,
                type="success")
        super(TodoView, self).update()

    @property
    @memoize
    def metromap(self):
        ''' Get the the metromap view
        '''
        return api.content.get_view(
            'metromap',
            self.workspace,
            self.request,
        )

    @property
    @memoize
    def milestone_options(self):
        ''' Get the milestone options from the metromap (if we have any)
        '''
        if not self.workspace:
            return None
        current_milestone = self.context.milestone
        return self.metromap.get_milestone_options(current_milestone)

    @property
    @memoize
    def allusers_json_url(self):
        ''' Return @@allusers.json in the proper context
        '''
        return '{}/@@allusers.json'.format(
            self.logical_parent.absolute_url()
        )

    def autosuggest_prefill(self, field):
        ''' Return JSON for pre-filling a pat-autosubmit field with the values for
        that field
        '''
        field_value = getattr(
            self.context,
            field,
            self.user and self.user.getId()
        )
        if not field_value:
            return
        users = imap(pi_api.userprofile.get, field_value.split(','))
        prefill = {
            user.getId(): user.fullname or user.getId()
            for user in users if user
        }
        if not prefill:
            return
        return dumps(prefill)

    def get_data_pat_autosuggest(self, fieldname):
        ''' Return the data-pat-autosuggest for a fieldname
        '''
        options = [
            'ajax-data-type: json',
            'maximum-selection-size: 1',
            'selection-classes: {}',
            'ajax-url: {}'.format(self.allusers_json_url),
            'allow-new-words: false',
        ]
        if (
            fieldname == 'initiator' and
            self.request.method == 'GET' and
            self.user
        ):
            prefill_json = self.autosuggest_prefill(fieldname)
            if prefill_json:
                options.append('prefill-json: {}'.format(prefill_json))

        return '; '.join(options)


class TodoSidebar(TodoView):
    ''' Return the proper sidebar depending if we are in a workspace or in a
    userprofile
    '''
    personal_task_sidebar = ViewPageTemplateFile(
        'templates/personal_task_sidebar.pt'
    )

    _navigation_tabs = OrderedDict(
        [
            ('@@all-tasks', _('All tasks')),
            ('@@my-tasks', _('My tasks')),
            ('@@personal-tasks', _('Personal tasks')),
        ]
    )

    def navigation_tabs(self):
        ''' Convenience method to easily render the tabs in the template
        '''
        base_url = self.logical_parent.absolute_url()
        items = [
            {
                'url': '{base_url}/{view}'.format(
                    base_url=base_url,
                    view=view,
                ),
                'label': label,
            } for view, label in self._navigation_tabs.iteritems()
        ]
        items[0]['klass'] = 'current'
        return items

    def __call__(self):
        ''' Choose the proper sidebar to render
        '''
        if not self.workspace:
            return self.personal_task_sidebar()
        view = api.content.get_view(
            'sidebar.default',
            self.workspace,
            self.request,
        )
        return view()


class TodoWorkflowMenu(WorkflowMenu):
    ''' Customize the workflow menu for todos
    '''
    _done_states = (
        'done',
    )

    @memoize
    def is_done(self):
        ''' Check if this todo is done
        '''
        return self.get_workflow_state() in self._done_states

    def form_pat_inject_options(self):
        ''' Return the data-path-inject options we want to use

        Adds the todo-${here/UID} element as an injection target
        '''
        template = ' && '.join((
            'url: {url}; source: #global-statusmessage; target: #global-statusmessage;',  # noqa
            'url: {url}; source: #workflow-menu; target: #workflow-menu;',
            'url: {url}; source: #todo-{uid}-replacement; target: #todo-{uid}; loading-class: \'\'',  # noqa
        ))
        return template.format(
            url=self.injection_url,
            uid=self.context.UID(),
        )
