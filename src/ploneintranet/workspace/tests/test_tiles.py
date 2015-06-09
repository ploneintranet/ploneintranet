# -*- coding: utf-8 -*-
from DateTime import DateTime
from plone import api
from ploneintranet.workspace.tests.test_views import BaseViewTest
from ploneintranet.microblog.interfaces import IMicroblogTool
from ploneintranet.microblog.statusupdate import StatusUpdate
from zope.component import queryUtility


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
        su = StatusUpdate(
            'Proposal draft V1.0 # This is a mock!!!',
            **{
                'context': self.workspace,
            }
        )
        su.id = 123456789L
        su.creator = 'charlotte_holzer'
        su.date = DateTime('2008/02/14 18:43')
        mb = queryUtility(IMicroblogTool)
        mb.add(su)
        workspaces = tile.workspaces()
        self.assertEqual(len(workspaces), 1)

        demo_ws = workspaces[0]
        activities = demo_ws['activities']
        self.assertEqual(len(activities), 1)
        self.assertDictEqual(
            activities[0],
            {
                'object': 'Proposal draft V1.0 # This is a mock!!!',
                'subject': 'charlotte_holzer',
                'time': {
                    'datetime': '2008-02-14',
                    'title': '14 February 2008, 18:43'
                },
                'verb': 'posted'
            }
        )
