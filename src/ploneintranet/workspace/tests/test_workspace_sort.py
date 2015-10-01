# coding=utf-8
"""
Tests for ploneintranet.workspace forms
"""
from plone import api
from ploneintranet.workspace.tests.base import BaseTestCase
from ploneintranet.workspace.browser.tiles.workspaces import my_workspaces


class TestWorkspaceSort(BaseTestCase):

    def test_workspace_sort(self):
        self.login_as_portal_owner()
        request = self.layer['request']

        for sort_by in ('alphabet', 'newest'):
            request.sort = sort_by
            ws_container = api.content.get_view(
                name='workspaces.html',
                context=self.portal.workspaces,
                request=request)
            self.assertEqual(len(ws_container.sort_options()), 2)
            self.assertEqual(ws_container.sort_options()[0]['value'],
                             'alphabet')

    def test_my_workspaces(self):
        ws_before = my_workspaces(self.portal.workspaces)
        api.content.create(
            self.portal.workspaces,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace')
        ws_after = my_workspaces(self.portal.workspaces)
        self.assertEqual(len(ws_after) - len(ws_before), 1)
