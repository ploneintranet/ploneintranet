# coding=utf-8
"""
Tests for ploneintranet.workspace forms
"""
from datetime import datetime
from plone import api
from ploneintranet import api as pi_api
from ploneintranet.workspace.tests.base import BaseTestCase
from ploneintranet.workspace.browser.tiles.workspaces import my_workspaces


class TestWorkspaceSort(BaseTestCase):

    def test_workspace_sort(self):
        self.login_as_portal_owner()
        request = self.layer['request']

        for sort_by in ('active', 'alphabet', 'newest'):
            request.sort = sort_by
            ws_container = api.content.get_view(
                name='workspaces.html',
                context=self.portal.workspaces,
                request=request)
            self.assertEqual(len(ws_container.sort_options()), 3)
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

    def test_my_workspaces_sorting(self):
        ''' This will test that:

        - sorting by default is by sortable_title
        - it can be by modification date (reversed)
        - it can be by activity date (reversed)
        - it can take any value and will not fail
        '''
        # create dummy stuff
        workspace_container = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacecontainer',
            'workspace-container-sorting',
            title='Workspace container sorting'
        )
        obj1 = api.content.create(
            workspace_container,
            'ploneintranet.workspace.workspacefolder',
            'sort1',
            title="Sortable 1",
        )
        obj1.modification_date = datetime.strptime('2015/01/01', '%Y/%m/%d')
        obj1.reindexObject(idxs=['modified'])
        obj2 = api.content.create(
            workspace_container,
            'ploneintranet.workspace.workspacefolder',
            'sort2',
            title="Sortable 2",
        )
        obj2.modification_date = datetime.strptime('2016/01/01', '%Y/%m/%d')
        obj2.reindexObject(idxs=['modified'])
        obj3 = api.content.create(
            workspace_container,
            'ploneintranet.workspace.workspacefolder',
            'sort3',
            title="Sortable 3",
        )
        obj3.modification_date = datetime.strptime('2015/07/01', '%Y/%m/%d')
        obj3.reindexObject(idxs=['modified'])

        # Create some status updates
        pi_api.microblog.statusupdate.create('test 3', microblog_context=obj3)

        # Check default query
        response = my_workspaces(
            workspace_container,
        )
        self.assertListEqual(
            [item['title'] for item in response],
            ['Sortable 1', 'Sortable 2', 'Sortable 3'],
        )

        # Check sort=alphabet
        response = my_workspaces(
            workspace_container,
            request={'sort': 'alphabet'},
        )
        self.assertListEqual(
            [item['title'] for item in response],
            ['Sortable 1', 'Sortable 2', 'Sortable 3'],
        )

        # Check sort=newest
        response = my_workspaces(
            workspace_container,
            request={'sort': 'newest'},
        )
        self.assertListEqual(
            [item['title'] for item in response],
            ['Sortable 2', 'Sortable 3', 'Sortable 1'],
        )

        # Check sort=activity
        response = my_workspaces(
            workspace_container,
            request={'sort': 'activity'},
        )
        self.assertEqual(response[0]['title'], 'Sortable 3')

        # Get rid of testing content
        api.content.delete(workspace_container)
