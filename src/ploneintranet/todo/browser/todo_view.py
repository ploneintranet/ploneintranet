# coding=utf-8
from ..interfaces import ITodoUtility
from logging import getLogger
from plone import api
from plone.app.blocks.interfaces import IBlocksTransformEnabled
from plone.memoize.view import memoize
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.layout.browser.workflow import WorkflowMenu
from ploneintranet.workspace.basecontent.baseviews import ContentView
from zope.component import getUtility
from zope.interface import implementer


log = getLogger(__name__)


class BaseView(ContentView):

    def __init__(self, context, request):
        super(BaseView, self).__init__(context, request)
        self.util = getUtility(ITodoUtility)
        self.current_user_id = api.user.get_current().getId()
        self.content_uid = api.content.get_uuid(self.context)


@implementer(IBlocksTransformEnabled)
class TodoView(BaseView):

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
        current_milestone = self.context.milestone
        return self.metromap.get_milestone_options(current_milestone)


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
