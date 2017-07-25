# -*- coding=utf-8 -*-
from AccessControl import Unauthorized
from plone import api
from plone.memoize.view import memoize
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.workspace.browser.add_content import AddBase
from ploneintranet.workspace.interfaces import IWorkspaceFolder
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class AddTask(AddBase):
    ''' The base add task in workspace view
    '''
    title = _('Create task')
    template = ViewPageTemplateFile('templates/add_task.pt')
    _form_data_pat_inject_parts = (
        '#workspace-tickets',
    )
    show_container_selector = True

    @property
    @memoize
    def allusers_json_url(self):
        ''' Return @@allusers.json in the proper context
        '''
        target = self.parent_workspace or self.context
        return '{}/@@allusers.json'.format(target.absolute_url())

    @property
    @memoize
    def milestone_options(self):
        ''' Get the milestone options from the metromap (if we have any)
        '''
        workspace = self.parent_workspace
        if not workspace:
            return
        metromap = api.content.get_view(
            'metromap',
            workspace,
            self.request,
        )
        return metromap.get_milestone_options()

    def redirect(self, url):
        workspace = self.parent_workspace
        if workspace:
            url = self.parent_workspace.absolute_url() + '?show_sidebar'
        return self.request.response.redirect(url)


class AppAddTask(AddTask):
    ''' Add a task from the app.

    The task can be a personal task or a workspace task
    '''
    form_data_pat_inject = None
    ok_closes_panel = False
    show_container_selector = True

    @property
    @memoize
    def possible_containers(self):
        ''' List the possible containers,
        i.e. the workspaces where we can add tasks.
        '''
        brains = api.content.find(
            context=self.workspace_container,
            object_provides=IWorkspaceFolder,
        )
        if len(brains) > 100:
            return brains
        workspaces = (brain.getObject() for brain in brains)
        return [
            workspace
            for workspace in workspaces
            if api.user.has_permission('Add portal content', obj=workspace)
        ]

    @property
    @memoize
    def milestone_options(self):
        container_path = self.request.get('container', '')
        container = container_path and api.content.get(container_path)
        if not container:
            return []
        view = api.content.get_view(
            'add_task',
            container,
            self.request,
        )
        return view.milestone_options

    def create(self, container=None):
        ''' Set up the proper container before creating the object
        '''
        if container == self.context:
            # If the container is the app we will want
            # to create the task in the user
            container = self.user
        return super(AppAddTask, self).create(container=container)

    def redirect(self, url):
        ''' Add a query string parameter that suggests to render the view
        in the app context
        '''
        url += '?app'
        return self.request.response.redirect(url)


class GetMilestonesForContainer(BrowserView):
    ''' Helper view that returns the milestones for a container
    '''
    def __call__(self):
        ''' Look for a container path in the request, get it an return
        the proper add form
        '''
        container_path = self.request.get('container', '')
        container = container_path and api.content.get(container_path)
        if (
            container and
            api.user.has_permission('Add portal content', obj=container)
        ):
            view = api.content.get_view(
                'add_task',
                container,
                self.request,
            )
            return view()
        raise Unauthorized(
            'Cannot get milestones for this container_path: %r' % (
                container_path
            )
        )
