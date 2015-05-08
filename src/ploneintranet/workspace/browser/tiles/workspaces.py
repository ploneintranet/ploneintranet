# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize.view import memoize
from plone.tiles import Tile
from ploneintranet.workspace.utils import my_workspaces


class WorkspacesTile(Tile):

    index = ViewPageTemplateFile("templates/workspaces.pt")

    @memoize
    def workspaces(self):
        """ The list of my workspaces
        """
        return my_workspaces(self.context)

    def render(self):
        return self.index()

    def __call__(self):
        return self.render()
