# -*- coding: utf-8 -*-
'''Setup/installation tests for this package.'''
from datetime import datetime
from DateTime import DateTime
from plone import api
from plone.mocktestcase import MockTestCase
from ploneintranet.calendar.browser.interfaces import IPloneintranetCalendarLayer  # noqa
from ploneintranet.calendar.browser.app import View as CalendarAppView
from ploneintranet.calendar.testing import IntegrationTestCase

from plone.app.testing.interfaces import SITE_OWNER_NAME
from plone.testing import z2

from ploneintranet.calendar.importexport import import_ics
from ploneintranet.calendar.browser.app import TZ_COOKIE_NAME

from ploneintranet.calendar.config import DEFAULT_TZ_ID
from ploneintranet.calendar.utils import tzid_from_dt
from ploneintranet.calendar.utils import get_pytz_timezone

from ploneintranet.calendar.utils import get_workspaces_of_current_user
from ploneintranet.calendar.utils import get_events_of_current_user
from ploneintranet.calendar.utils import get_calendars

from ploneintranet.calendar.browser.tiles import FullCalendarTile


from pytz import timezone

PROJECTNAME = 'ploneintranet.calendar'


class TestCalendar(IntegrationTestCase, MockTestCase):
    """ """

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.login_as_portal_owner()
        self.workspace = api.content.create(
            container=self.portal['workspaces'],
            type='ploneintranet.workspace.workspacefolder',
            title='Event import workspace',
        )

    def login_as_portal_owner(self):
            """
            helper method to login as site admin
            """
            z2.login(self.layer['app']['acl_users'], SITE_OWNER_NAME)

    def test_calendar_ics_import(self):
        imported = import_ics(self.workspace, TEST_ICS)
        self.assertEqual(imported, 5)
        self.event = None

    #
    # app.py
    #
    def test_get_workspaces_query_string(self):

        self.request.set('workspaces', ['workspace1', 'workspace2'])
        self.request.set('all-cals', 'on')
        view = CalendarAppView(self.portal.apps.calendar, self.request)
        qs = view.get_workspaces_query_string()
        self.assertNotEqual(qs, '')
        self.assertTrue('workspace1' in qs)
        self.assertTrue('workspace2' in qs)
        self.assertTrue('all-cals:boolean=True' in qs)

    def test_get_timezone_data(self):
        view = CalendarAppView(self.portal.apps.calendar, self.request)
        data = view.get_timezone_data()
        # assuming we should have many, but they can grow over time
        self.assertTrue(len(data) > 80)
        berlin = [x for x in data if x['zone'] == 'Europe/Berlin'][0]
        self.assertTrue('Berlin' in berlin['name'])

    def test_timezone_cookie(self):
        view = CalendarAppView(self.portal.apps.calendar, self.request)
        self.assertTrue(TZ_COOKIE_NAME not in self.request.RESPONSE.cookies)
        tz = view.get_user_timezone()
        self.assertTrue(tz == 'Europe/Berlin')

        view.set_user_timezone('Asia/Kabul')

        self.assertTrue(TZ_COOKIE_NAME in self.request.RESPONSE.cookies)
        self.assertTrue(
            self.request.RESPONSE.cookies[TZ_COOKIE_NAME]['value'] ==
            'Asia/Kabul')

        # Fake roundtrip to set the cookie
        self.request.set(TZ_COOKIE_NAME, 'US/East-Indiana')
        tz = view.get_user_timezone()
        self.assertTrue(tz == 'US/East-Indiana')

    def test_id2class(self):
        view = CalendarAppView(self.portal.apps.calendar, self.request)
        self.assertTrue(
            view.id2class('my-w:o+rk.s(p)a&ce') == 'my-work-space')

    #
    # fullcalendar tile
    #
    def test_get_start_date(self):
        tile = FullCalendarTile(self.portal.apps.calendar, self.request)
        self.assertTrue(
            tile.get_start_date() == datetime.now().strftime("%Y-%m-%d"))

        self.request.form['day'] = '31'
        self.request.form['month'] = '04'
        self.request.form['year'] = '1000'
        tile = FullCalendarTile(self.portal.apps.calendar, self.request)
        self.assertTrue(
            tile.get_start_date() == "1000-04-31")

    def test_format_date_time(self):
        tile = FullCalendarTile(self.portal.apps.calendar, self.request)
        dt = datetime.now()
        DT = DateTime()  # noqa
        fmt = tile._format_date_time(DT, False)

        fmt = tile._format_date_time(dt, is_whole_day=True)
        self.assertTrue(
            fmt[0] == dt.strftime('%Y-%m-%d'))
        self.assertTrue(
            fmt[1] == dt.strftime('%d %B %Y'))

        # Also test DateTime to datetime conversion
        fmt = tile._format_date_time(DT, is_whole_day=False)
        self.assertTrue(
            fmt[0] == dt.strftime('%Y-%m-%dT%H:%MZ'))
        self.assertTrue(
            ", " in fmt[1])

    def test_get_event_class(self):
        tile = FullCalendarTile(self.portal.apps.calendar, self.request)
        event = self.create_dummy(
            __parent__=self.workspace,
            __name__=None,
            title="My event",
            absolute_url=lambda: self.workspace.absolute_url() + '/my-event',
            url=self.workspace.absolute_url() + '/my-event',
            ws_type='workspace',
            start=DateTime(),
            end=DateTime() + 1,
            whole_day=True)

        classes = tile._get_event_class(event, 'other')

        self.assertTrue(
            'cal-cat-event-import-workspace' in classes)
        self.assertTrue(
            'cal-cat-event-import-workspace-other' in classes)
        self.assertTrue(
            'all-day' in classes)
        self.assertTrue(
            'cal-cat-workspace' in classes)
        self.assertTrue(
            'cal-cat-workspace-other' in classes)
    #
    # utils
    #

    def test_tzid_from_dt(self):
        self.assertTrue(tzid_from_dt(datetime.now()) == DEFAULT_TZ_ID)

        amsterdam = timezone('Europe/Amsterdam')
        now_in_ams = amsterdam.localize(datetime.now())

        self.assertTrue(tzid_from_dt(now_in_ams) == 31)

    def test_get_pytz_timezone(self):
        self.assertTrue(get_pytz_timezone(30).zone == "Europe/London")

    def test_get_calendars(self):
        cal_data = get_calendars(self.portal)
        calendars = cal_data['calendars']
        self.assertTrue(len(calendars['my']) == 0)
        self.assertTrue(len(calendars['personal']) == 0)
        self.assertTrue(len(calendars['invited']) == 0)
        self.assertTrue(len(calendars['public']) == 0)
        self.assertTrue(len(calendars['other']) == 0)

        # Todo: Add events, invite user, assert that calendars appear
        # XXX: Need solr layer to test this.

    def test_get_workspaces_of_current_user(self):
        # Todo: Add events, invite user, assert that calendars appear
        # XXX: Need solr layer to test this.
        # For now, at least run it
        get_workspaces_of_current_user(self.portal)

    def test_get_events_of_current_user(self):
        # Todo: Add events, invite user, assert that calendars appear
        # XXX: Need solr layer to test this.
        # For now, at least run it
        get_events_of_current_user(self.portal)

    #
    # Teardown
    #
    def tearDown(self):
        self.login_as_portal_owner()
        api.content.delete(self.workspace)

TEST_ICS = u"""
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Plone.org//NONSGML plone.app.event//EN
X-WR-CALDESC:this is a test description
X-WR-CALNAME:testevent
X-WR-RELCALID:48f1a7ad64e847568d860cd092344970
X-WR-TIMEZONE:Europe/Vienna
BEGIN:VTIMEZONE
TZID:Europe/Vienna
X-LIC-LOCATION:Europe/Vienna
BEGIN:DAYLIGHT
DTSTART;VALUE=DATE-TIME:20130331T030000
TZNAME:CEST
TZOFFSETFROM:+0100
TZOFFSETTO:+0200
END:DAYLIGHT
END:VTIMEZONE

BEGIN:VEVENT
SUMMARY:e1
DESCRIPTION:A bäsic event with many pråperties.
DTSTART;TZID=Europe/Vienna;VALUE=DATE-TIME:20130719T120000
DTEND;TZID=Europe/Vienna;VALUE=DATE-TIME:20130720T130000
DTSTAMP;VALUE=DATE-TIME:20130719T125936Z
UID:48f1a7ad64e847568d860cd092344970
ATTENDEE;CN=attendee1;ROLE=REQ-PARTICIPANT:attendee1
ATTENDEE;CN=attendee2;ROLE=REQ-PARTICIPANT:attendee2
ATTENDEE;CN=attendee3;ROLE=REQ-PARTICIPANT:attendee3
CONTACT:Tést Contact Näme\, 1234\, test@contact.email\, http://test.url
CREATED;VALUE=DATE-TIME:20130719T105931Z
LAST-MODIFIED;VALUE=DATE-TIME:20130719T105931Z
LOCATION:Optimolwerke\, Friedenstraße\, Munich\, Germany
URL:http://localhost:8080/Plone/testevent
END:VEVENT

BEGIN:VEVENT
SUMMARY:e2
DESCRIPTION:A recurring event with exdates
DTSTART:19960401T010000
DTEND:19960401T020000
RRULE:FREQ=DAILY;COUNT=100
EXDATE:19960402T010000Z,19960403T010000Z,19960404T010000Z
UID:48f1a7ad64e847568d860cd0923449702
LAST-MODIFIED;VALUE=DATE-TIME:20130719T105931Z
END:VEVENT

BEGIN:VEVENT
SUMMARY:e3
DESCRIPTION:A Recurring event with multiple exdates, one per line.
DTSTART;TZID=Europe/Vienna:20120327T100000
DTEND;TZID=Europe/Vienna:20120327T180000
RRULE:FREQ=WEEKLY;UNTIL=20120703T080000Z;BYDAY=TU
EXDATE;TZID=Europe/Vienna:20120529T100000
EXDATE;TZID=Europe/Vienna:20120403T100000
EXDATE;TZID=Europe/Vienna:20120410T100000
EXDATE;TZID=Europe/Vienna:20120501T100000
EXDATE;TZID=Europe/Vienna:20120417T100000
DTSTAMP:20130716T120638Z
UID:48f1a7ad64e847568d860cd0923449703
LAST-MODIFIED;VALUE=DATE-TIME:20130719T105931Z
END:VEVENT

BEGIN:VEVENT
SUMMARY:e4
DESCRIPTION:Whole day event
DTSTART:20130404
DTEND:20130404
UID:48f1a7ad64e847568d860cd0923449704
LAST-MODIFIED;VALUE=DATE-TIME:20130719T105931Z
END:VEVENT

BEGIN:VEVENT
SUMMARY:e5
DESCRIPTION:Open end event
DTSTART:20130402T120000
UID:48f1a7ad64e847568d860cd0923449705
LAST-MODIFIED;VALUE=DATE-TIME:20130719T105931Z
END:VEVENT

END:VCALENDAR
"""
