# coding=utf-8
from json import loads
from plone import api
from ploneintranet.layout.testing import IntegrationTestCase


class TestViews(IntegrationTestCase):

    def setUp(self):
        ''' Custom shared utility setup for tests.
        '''
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_date_picker_i18n_json(self):
        ''' We want pat-date-picker i18n
        '''
        view = api.content.get_view(
            'date-picker-i18n.json',
            self.portal,
            self.request,
        )
        observed = loads(view())
        expected = {
            u'nextMonth': u'next_month_link',
            u'previousMonth': u'prev_month_link',
            u'months': [
                u'January',
                u'February',
                u'March',
                u'April',
                u'May',
                u'June',
                u'July',
                u'August',
                u'September',
                u'October',
                u'November',
                u'December'
            ],
            u'weekdays': [
                u'Sunday',
                u'Monday',
                u'Tuesday',
                u'Wednesday',
                u'Thursday',
                u'Friday',
                u'Saturday'
            ],
            u'weekdaysShort': [
                u'Sun',
                u'Mon',
                u'Tue',
                u'Wed',
                u'Thu',
                u'Fri',
                u'Sat'
            ]
        }
        self.assertDictEqual(
            observed,
            expected,
        )

    def test_dashboard_tiles(self):
        ''' Check if the dashboard tiles are correctly configured
        through the registry
        '''
        view = api.content.get_view(
            'dashboard.html',
            self.portal,
            self.request,
        )
        self.assertTupleEqual(
            view.activity_tiles(),
            (
                u'./@@contacts_search.tile',
                u'./@@news.tile',
                u'./@@my_documents.tile',
            )
        )
        self.assertTupleEqual(
            view.task_tiles(),
            (
                u'./@@contacts_search.tile',
                u'./@@news.tile',
                u'./@@my_documents.tile',
                u'./@@workspaces.tile?workspace_type=ploneintranet.workspace.workspacefolder',  # noqa
                u'./@@workspaces.tile?workspace_type=ploneintranet.workspace.case',   # noqa
                u'./@@events.tile',
                u'./@@tasks.tile',
            )
        )

    def test_apps_view(self):
        ''' Check the @@apps view
        '''
        view = api.content.get_view(
            'apps.html',
            self.portal,
            self.request,
        )
        self.assertListEqual(
            [tile.sorting_key for tile in view.tiles()],
            [
                (10, u'contacts'),
                (20, u'messages'),
                (30, u'todo'),
                (40, u'calendar'),
                (50, u'slide-bank'),
                (60, u'image-bank'),
                (70, u'news'),
                (80, u'case-manager'),
                (90, u'app-market'),
            ]
        )
