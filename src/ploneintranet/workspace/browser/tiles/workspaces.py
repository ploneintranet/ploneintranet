# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.memoize.view import memoize
from plone.tiles import Tile


class WorkspacesTile(Tile):

    index = ViewPageTemplateFile("templates/workspaces.pt")

    def get_workspace_activities(self, brain, limit=1):
        ''' Return the workspace activities sorted by reverse chronological
        order

        Regarding the time value:
         - the datetime value contains the time in international format
           (machine readable)
         - the title value contains the absolute date and time of the post
        '''
        # BBB: this is a mock!!!!
        return [
            {
                'subject': 'Charlotte Holzer',
                'verb': 'published',
                'object': 'Proposal draft V1.0 # This is a mock!!!',
                'time': {
                    'datetime': '2008-02-14',
                    'title': '5 October 2015, 18:43',
                }
            }
        ][:limit]

    @memoize
    def workspaces(self):
        ''' The list of my workspaces
        '''
        pc = api.portal.get_tool('portal_catalog')
        brains = pc(
            portal_type="ploneintranet.workspace.workspacefolder",
            sort_on="modified",
            sort_order="reversed",
        )
        workspaces = [
            {
                'title': brain.Title,
                'description': brain.Description,
                'url': brain.getURL(),
                'activities': self.get_workspace_activities(brain),
            } for brain in brains
        ]
        return workspaces

    def render(self):
        return self.index()

    def __call__(self):
        return self.render()
