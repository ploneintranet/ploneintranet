# coding=utf-8
from plone import api
from plone.memoize.view import memoize_contextless
from plone.tiles import Tile
from ploneintranet.layout.app import apps_container_id
from datetime import datetime
from datetime import timedelta
from DateTime import DateTime
from ploneintranet.workspace.utils import parent_workspace
from ploneintranet.workspace.interfaces import IBaseWorkspaceFolder
from AccessControl.security import checkPermission
from Products.CMFCore.permissions import ModifyPortalContent
from zope.component import getUtility
from ploneintranet.search.interfaces import ISiteSearch
from scorched.dates import solr_date
from plone.app.contenttypes.interfaces import IEvent
from plone.app.event.base import localized_now
from plone.event.interfaces import IEventAccessor


class FullCalendarTile(Tile):
    '''FullCalendar as a tile, used in cal app and workspace calendar'''

    @property
    def app(self):
        portal = api.portal.get()
        return getattr(portal, apps_container_id).calendar

    @property
    @memoize_contextless
    def app_url(self):
        return self.app.absolute_url()

    @property
    def today(self):
        return "saturday, 10 sept 2016"

    @property
    @memoize_contextless
    def app_calendar(self):
        ''' Return the calendar app that will be displayed in the tile
        '''
        return api.content.get_view(
            'app-calendar',
            self.app,
            self.request,
        )

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

    # @ram.cache(event_cache_key)
    def get_event_class(self, event):
        """take the classes and add alien if appropriate in context"""
        return ''  # XX see star.theme.userdata line 77ff

        ws = parent_workspace(self.context)
        wsid = "cal-cat-{0}".format(ws.id)
        classes = set(event.get('classes', '').split(' '))
        if IBaseWorkspaceFolder.providedBy(ws):
            if wsid not in classes:
                classes.add('cal-cat-alien')
            classes.add("cal-cat-%s" % ws.ws_type)

        if checkPermission(ModifyPortalContent, self.context):
            classes.add('editable')
        return " ".join(classes)

    def _format_date_time(self, date_time, is_whole_day):
        if isinstance(date_time, DateTime):
            date_time = date_time.asdatetime()
        # 2012-02-18T09:00Z
        date_time_short = date_time.strftime('%Y-%m-%d')
        # 18 February 2012, 9:00
        date_time_long = date_time.strftime('%d %B %Y')

        if not is_whole_day:
            time = date_time.strftime("%H:%M%z")
            date_time_short += "T" + time
            date_time_long += ", " + time

        return (date_time_short, date_time_long)

    def get_event_date_times(self, event):
        # XXXYYY Too slow, index that!!!
        event_accessor = IEventAccessor(event.getObject())
        is_whole_day = event_accessor.whole_day
        event_dtimes = {}
        if event_accessor.start:

            (event_dtimes["start_date_time_short"],
             event_dtimes["start_date_time_long"]) = self._format_date_time(
                 event_accessor.start, is_whole_day)
        if event_accessor.end:
            (event_dtimes["end_date_time_short"],
             event_dtimes["end_date_time_long"]) = self._format_date_time(
                 event_accessor.end, is_whole_day)

        return event_dtimes

    def get_events(self):
        """ Load events from solr """
        # We only provide a history of 30 days, otherwise, fullcalendar has
        # too much to render. This could be made more flexible
        evt_date = localized_now() - timedelta(30)
        query = dict(object_provides=IEvent.__identifier__,
                     end__gt=solr_date(evt_date))

        include_archived = self.request.get('archived', False)
        if not include_archived:
            query['is_archived'] = False

        sitesearch = getUtility(ISiteSearch)
        response = sitesearch.query(filters=query, step=99999)
        return response
