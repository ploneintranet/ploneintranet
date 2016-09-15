# -*- coding: utf-8 -*-
import icalendar
import pytz

from datetime import datetime
from datetime import time
from plone import api
from ploneintranet.calendar.utils import tzid_from_dt


def ical2vsevent(ical):
    dtstart = ical['DTSTART'].dt
    if 'DTEND' in ical:
        dtend = ical['DTEND'].dt
    elif 'DURATION' in ical:
        dtend = dtstart + ical['DURATION']
    else:
        dtend = dtstart

    if isinstance(dtstart, datetime):
        all_day = False
        tzid = tzid_from_dt(dtstart)
    else:
        # All-day event:
        all_day = True
        tz = pytz.timezone('Europe/Berlin')
        tzid = 31
        dtstart = tz.localize(datetime.combine(dtstart, time(0, 0, 0)))
        dtend = tz.localize(datetime.combine(dtend, time(23, 59, 59)))

    if 'SUMMARY' in ical:
        title = unicode(ical['SUMMARY'])
    else:
        title = "Imported event"

    if 'DESCRIPTION' in ical:
        description = unicode(ical['DESCRIPTION'])
    else:
        description = ''

    if 'LOCATION' in ical:
        location = unicode(ical['LOCATION'])
    else:
        location = ''

    return {
        'title': title,
        'description': description,
        'location': location,
        'startDate': dtstart,
        'endDate': dtend,
        'timezone': tzid,
        'all_day': all_day,
        'id': unicode(ical['UID']),
    }


def import_ics(context, ics_data):
    calendar = icalendar.Calendar.from_ical(ics_data)
    count = 0
    for component in calendar.subcomponents:
        if isinstance(component, icalendar.Event):
            data = ical2vsevent(component)
            api.content.create(container=context,
                               type='Event',
                               **data)
            count += 1
    return count
