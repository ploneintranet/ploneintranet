# coding=utf-8
from collections import defaultdict
from DateTime import DateTime
from datetime import datetime
from plone import api
from plone.memoize.view import memoize
from plone.tiles import Tile
from ploneintranet.calendar.config import TZ_COOKIE_NAME
from ploneintranet.calendar.utils import escape_id_to_class
from ploneintranet.calendar.utils import get_timezone_info
from ploneintranet.layout.app import apps_container_id
from ploneintranet.workspace.indexers import timezone as timezone_indexer
from ploneintranet.workspace.interfaces import IBaseWorkspaceFolder
from ploneintranet.workspace.utils import parent_workspace
from Products.CMFCore.permissions import ModifyPortalContent
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

import os
import pytz


class FullCalendarTile(Tile):
    '''FullCalendar as a tile, used in cal app and workspace calendar'''

    @memoize
    def workspace(self):
        return parent_workspace(self.context)

    @property
    def app(self):
        portal = api.portal.get()
        return getattr(portal, apps_container_id).calendar

    @property
    def today(self):
        now = datetime.now()
        return now.strftime("%a, %d %b %Y")

    def get_start_date(self):
        current_date = datetime.now()
        current_day = current_date.day
        current_month = current_date.month
        current_year = current_date.year
        try:
            day = int(self.request.form.get("day") or current_day)
        except ValueError:
            day = current_day
        try:
            month = int(self.request.form.get("month") or current_month)
        except ValueError:
            month = current_month
        try:
            year = int(self.request.form.get("year") or current_year)
        except ValueError:
            year = current_year
        datestr = "{year}-{month:0=2}-{day:0=2}".format(year=year,
                                                        month=month,
                                                        day=day)
        return datestr

    def _format_date_time(self, date_time, is_whole_day, timezone=None):
        if isinstance(date_time, DateTime):
            date_time = date_time.asdatetime()
        if timezone is not None:
            date_time = date_time.astimezone(timezone)
        # 2012-02-18T09:00Z
        format_short = '%Y-%m-%d'
        # 18 February 2012, 9:00
        format_long = '%d %B %Y'

        if not is_whole_day:
            format_short = format_short + 'T%H:%M'
            format_long = format_long + ', %H:%M'
            if timezone is not None:
                format_short += '%z'
                format_long += ' %Z'
            else:
                format_short += 'Z'
        date_time_short = date_time.strftime(format_short)
        date_time_long = date_time.strftime(format_long)
        return (date_time_short, date_time_long)

    def _get_event_date_times(self, event):
        is_whole_day = event.whole_day
        timezone = event.timezone
        if isinstance(timezone, bool):
            # do not break badly if the timezone is not indexed
            timezone = timezone_indexer(event.getObject())()
        if timezone is not None:
            timezone = pytz.timezone(timezone)
        event_dtimes = {}
        if event.start:
            (event_dtimes["start_date_time_short"],
             event_dtimes["start_date_time_long"]) = self._format_date_time(
                 event.start, is_whole_day, timezone)
        if event.end:
            (event_dtimes["end_date_time_short"],
             event_dtimes["end_date_time_long"]) = self._format_date_time(
                 event.end, is_whole_day, timezone)

        return event_dtimes

    @memoize
    def can_edit(self):
        ''' Check edit permission on this context
        '''
        return api.user.has_permission(ModifyPortalContent, obj=self.context)

    def _get_event_class(self, event, calendar=None):
        """take the classes and add alien if appropriate in context"""

        classes = set(('cal-event',))

        # This assumes that an event always is placed right within a workspace.
        # Reason: Obviously getting the event and its workspace is expensive
        # and ading an index for it seems too much as well, but can be done if
        # this assumption proves to be not valid anymore.
        path = event.url
        workspace_id = path.split('/')[-2]
        classes.add("cal-cat-{0}".format(workspace_id))

        is_whole_day = event.whole_day
        if is_whole_day:
            classes.add('all-day')

        classes.add("cal-cat-{0}".format(event.ws_type))
        if calendar:
            classes.add("cal-cat-{0}-{1}".format(workspace_id, calendar))
            classes.add("cal-cat-{0}-{1}".format(event.ws_type, calendar))

        current_ws = self.workspace()
        if current_ws is not None and \
           IBaseWorkspaceFolder.providedBy(current_ws):
            if current_ws.id != workspace_id:
                classes.add('cal-cat-alien')

        if self.can_edit():
            classes.add('editable')

        return " ".join(classes)

    def get_events(self):
        """ get events for calendar, provide proper classes """
        # Get all the users workspaces
        # Get all the users events
        # sort the workspaces depending on events available and the users
        # rights within the workspaces and invitee status on the event
        app_view = api.content.get_view(
            self.app.app.lstrip('@'),
            self.app,
            self.request
        )

        groups = set(app_view.get_authenticated_groupids())
        w_by_path = {w.getPath(): w for w in app_view.get_workspaces()}
        all_events = app_view.get_authenticated_events()
        events_by_calendar = defaultdict(list)

        for e in all_events:
            ws_path = os.path.dirname(e.getPath())
            if ws_path not in w_by_path:
                # The immediate parent of this is event is not a workspace:
                # should not happen, we ignore it
                continue

            is_invited = groups.intersection(set(e.invitees or []))
            is_public = e.context.get('globalEvent', False)

            # Actually I can see all calendars which I have access to.
            # Plus I get a special section with calendars that have events I'm
            # invited to.
            # The concepts of public, personal and other seems deprecated
            if is_invited:
                events_by_calendar['invited'].append(e)
            elif is_public:
                events_by_calendar['public'].append(e)
            else:
                # Everything I can see
                events_by_calendar['my'].append(e)

        def enrich(event, calendar=None):
            classes = self._get_event_class(event, calendar)
            edict = {}
            # Create a dict representation of the search results
            # XXX: This is something to be done properly once we
            # abstract use of solr into the pi_api
            edict = event.context.copy()
            edict.update(event.__dict__.copy())
            del edict['context']
            del edict['response']
            edict['classes'] = classes
            edict['url'] = event.url
            edict.update(self._get_event_date_times(event))
            return edict

        events = []
        for calendar in events_by_calendar:
            ev_by_cal = events_by_calendar[calendar]
            for event in ev_by_cal:
                events.append(enrich(event, calendar))

        return events

    def get_timezone_data(self):
        timezone_vocab = getUtility(IVocabularyFactory,
                                    'ploneintranet.calendar.timezones')
        timezone_data = []
        for item in timezone_vocab:
            zoneinfo = get_timezone_info(item.token)
            timezone_data.append(zoneinfo)
        return timezone_data

    def get_user_timezone(self):
        return self.get_timezone_cookie(self)

    def set_user_timezone(self, tz):
        self.set_timezone_cookie(self, tz)

    def get_timezone_cookie(self, context):
        return context.request.get(TZ_COOKIE_NAME, 'Europe/Berlin')

    def set_timezone_cookie(self, context, tz):
        if tz:
            cookie_path = '/' + api.portal.get().absolute_url(1)
            context.request.response.setCookie(TZ_COOKIE_NAME, tz,
                                               path=cookie_path)

    def id2class(self, cal):
        return escape_id_to_class(cal)
