# -*- coding: utf-8 -*-
from plone import api
from ploneintranet.workspace.tests.test_views import BaseViewTest


class TestTiles(BaseViewTest):

    def test_workspace_tile(self):
        ''' This will test the existence of the workspaces.tile
        and its functionality
        '''
        tile = api.content.get_view(
            'workspaces.tile',
            self.portal,
            self.request
        )

        workspaces = tile.workspaces()
        self.assertEqual(len(workspaces), 1)

        demo_ws = workspaces[0]
        activities = demo_ws['activities']
        self.assertEqual(len(activities), 1)

        self.assertDictEqual(
            activities[0],
            {
                'object': 'Proposal draft V1.0 # This is a mock!!!',
                'subject': 'Charlotte Holzer',
                'time': {
                    'datetime': '2008-02-14',
                    'title': '5 October 2015, 18:43'
                },
                'verb': 'published'
            }
        )
