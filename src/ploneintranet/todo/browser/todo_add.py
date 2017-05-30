# -*- coding=utf-8 -*-
from plone import api
from plone.memoize.view import memoize
from ploneintranet.workspace.browser.add_content import AddBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class AddTask(AddBase):
    ''' The base add task in workspace view
    '''

    template = ViewPageTemplateFile('templates/add_task.pt')
    form_class = 'pat-inject'
    form_data_pat_inject = '#workspace-tickets'
    ok_closes_panel = True

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


class AddPersonalTask(AddTask):
    ''' Add a personal task from the app
    '''
    form_class = None
    form_data_pat_inject = None
    ok_closes_panel = False

    def redirect(self, url):
        return self.request.response.redirect(url)


class AddWorkspaceTask(AddPersonalTask):
    ''' Add a workspace task from the app
    '''
