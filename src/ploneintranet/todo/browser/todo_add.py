# -*- coding=utf-8 -*-
from plone import api
from plone.memoize.view import memoize
from ploneintranet.workspace.browser.add_content import AddBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class AddTask(AddBase):

    template = ViewPageTemplateFile('templates/add_task.pt')

    @property
    @memoize
    def milestone_options(self):
        ''' Get the milestone options from the metromap (if we have any)
        '''
        metromap = api.content.get_view(
            'metromap',
            self.parent_workspace,
            self.request,
        )
        return metromap.get_milestone_options()

    def redirect(self, url):
        url = self.parent_workspace.absolute_url() + '?show_sidebar'
        return self.request.response.redirect(url)
