# -*- coding: utf-8 -*-
from DateTime import DateTime
from plone import api
from ploneintranet.workspace.tests.test_views import BaseViewTest
from ploneintranet.microblog.interfaces import IMicroblogTool
from ploneintranet.microblog.statusupdate import StatusUpdate
from zope.component import queryUtility
from zope.i18nmessageid.message import Message


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
                'microblog_context': self.workspace,
            }
        )
        su.id = 123456789L
        su.creator = 'charlotte_holzer'
        su.date = DateTime('2008/02/14 18:43')
        mb = queryUtility(IMicroblogTool)
        mb.add(su)
        workspaces = tile.workspaces(include_activities=True)
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
                    'datetime': su.date.strftime('%Y-%m-%d'),
                    'title': su.date.strftime('%d %B %Y, %H:%M'),
                    'timestamp': su.date.strftime('%s'),
                },
                'verb': 'posted'
            }
        )

    def test_workspace_tile_properties(self):
        ''' We have some request dependendent properties.
        We want to check they behave well.
        '''
        tile = api.content.get_view(
            'workspaces.tile',
            self.portal,
            self.request.clone()
        )
        self.assertEqual(self.portal.translate(tile.title), u'Workspaces')
        self.assertListEqual(
            tile.workspace_type,
            tile.available_workspace_types
        )
        self.assertEqual(tile.workspaces_url, 'http://nohost/plone/workspaces')

        # test requesting a request specifying a workspace type
        tile.request = self.request.clone()
        tile.request.form['workspace_type'] = 'ploneintranet.workspace.case'
        self.assertEqual(tile.title, u'tile_ploneintranet.workspace.case')
        self.assertIsInstance(tile.title, Message)
        self.assertEqual(tile.workspace_type, 'ploneintranet.workspace.case')
        self.assertEqual(
            tile.workspaces_url,
            (
                'http://nohost/plone/workspaces/'
                '?workspace_type=ploneintranet.workspace.case'
            )
        )

        # test requesting a request specifying a workspace type and a title
        tile.request = self.request.clone()
        tile.request.form['workspace_type'] = 'ploneintranet.workspace.case'
        tile.request.form['title'] = 'My workspace portlet'
        self.assertEqual(tile.title, u'My workspace portlet')
        self.assertIsInstance(tile.title, Message)
        self.assertEqual(tile.workspace_type, 'ploneintranet.workspace.case')
        self.assertEqual(
            tile.workspaces_url,
            (
                'http://nohost/plone/workspaces/'
                '?workspace_type=ploneintranet.workspace.case'
            )
        )

        # test requesting a request specifying a multiple workspace types
        tile.request = self.request.clone()
        tile.request.form['workspace_type'] = ['foo', 'bar']
        self.assertEqual(self.portal.translate(tile.title), u'Workspaces')
        self.assertListEqual(tile.workspace_type, ['foo', 'bar'])
        self.assertEqual(tile.workspaces_url, 'http://nohost/plone/workspaces')
