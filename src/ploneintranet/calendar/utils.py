# -*- coding: utf-8 -*-
import os
import pytz
from collections import defaultdict
from datetime import datetime
from datetime import timedelta

from plone import api
from plone.app.contenttypes.interfaces import IEvent
from plone.app.event.base import localized_now

from ploneintranet.search.interfaces import ISiteSearch
from ploneintranet.workspace.interfaces import IBaseWorkspaceFolder

from scorched.dates import solr_date

from vocabularies import timezone_list
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility

from .config import DEFAULT_TZ_ID

daylight_saving = {
    1: 0,
    2: 0,
    3: 0,
    4: 1,
    5: 1,
    6: 1,
    7: 0,
    8: 1,
    9: 1,
    10: 0,
    11: 1,
    12: 1,
    13: 0,
    14: 0,
    15: 1,
    16: 1,
    17: 0,
    18: 1,
    19: 0,
    20: 1,
    21: 1,
    22: 1,
    23: 0,
    24: 1,
    25: 1,
    26: 1,
    27: 0,
    28: 1,
    29: 0,
    30: 1,
    31: 1,
    32: 1,
    33: 1,
    34: 1,
    35: 1,
    36: 1,
    37: 1,
    38: 1,
    39: 1,
    40: 0,
    41: 1,
    42: 1,
    43: 1,
    44: 1,
    45: 0,
    46: 1,
    47: 0,
    48: 0,
    49: 1,
    50: 0,
    51: 1,
    52: 1,
    53: 0,
    54: 1,
    55: 0,
    56: 0,
    57: 0,
    58: 0,
    59: 1,
    60: 0,
    61: 0,
    62: 0,
    63: 1,
    64: 0,
    65: 0,
    66: 0,
    67: 0,
    68: 0,
    69: 0,
    70: 0,
    71: 1,
    72: 0,
    73: 0,
    74: 0,
    75: 1,
    76: 1,
    77: 0,
    78: 1,
    79: 1,
    80: 1,
    81: 0,
    82: 0,
}


pytz_zone = {
    # REMOVED: 1: pytz.timezone('Etc/GMT-12')
    2: pytz.timezone('Pacific/Midway'),
    3: pytz.timezone('US/Hawaii'),
    4: pytz.timezone('US/Alaska'),
    5: pytz.timezone('US/Pacific'),
    6: pytz.timezone('America/Tijuana'),
    7: pytz.timezone('US/Arizona'),
    8: pytz.timezone('America/Chihuahua'),
    9: pytz.timezone('US/Mountain'),
    10: pytz.timezone('America/Guatemala'),
    11: pytz.timezone('US/Central'),
    12: pytz.timezone('America/Mexico_City'),
    13: pytz.timezone('Canada/Saskatchewan'),
    14: pytz.timezone('America/Bogota'),
    15: pytz.timezone('US/Eastern'),
    16: pytz.timezone('US/East-Indiana'),
    17: pytz.timezone('America/Caracas'),
    18: pytz.timezone('Canada/Atlantic'),
    19: pytz.timezone('America/Manaus'),
    20: pytz.timezone('America/Santiago'),
    21: pytz.timezone('Canada/Newfoundland'),
    22: pytz.timezone('America/Sao_Paulo'),
    23: pytz.timezone('America/Argentina/Buenos_Aires'),
    24: pytz.timezone('America/Godthab'),
    25: pytz.timezone('America/Montevideo'),
    26: pytz.timezone('Atlantic/Azores'),
    27: pytz.timezone('Atlantic/Cape_Verde'),
    28: pytz.timezone('Atlantic/Azores'),
    29: pytz.timezone('Africa/Casablanca'),
    30: pytz.timezone('Europe/London'),
    31: pytz.timezone('Europe/Berlin'),
    32: pytz.timezone('Europe/Belgrade'),
    33: pytz.timezone('Europe/Brussels'),
    34: pytz.timezone('Europe/Sarajevo'),
    35: pytz.timezone('Africa/Algiers'),
    36: pytz.timezone('Asia/Amman'),
    37: pytz.timezone('Europe/Athens'),
    38: pytz.timezone('Asia/Beirut'),
    39: pytz.timezone('Africa/Cairo'),
    40: pytz.timezone('Africa/Harare'),
    41: pytz.timezone('Europe/Helsinki'),
    42: pytz.timezone('Asia/Jerusalem'),
    43: pytz.timezone('Europe/Minsk'),
    44: pytz.timezone('Africa/Windhoek'),
    45: pytz.timezone('Asia/Kuwait'),
    46: pytz.timezone('Europe/Moscow'),
    47: pytz.timezone('Africa/Nairobi'),
    48: pytz.timezone('Asia/Tbilisi'),
    49: pytz.timezone('Asia/Tehran'),
    50: pytz.timezone('Asia/Muscat'),
    51: pytz.timezone('Asia/Baku'),
    52: pytz.timezone('Asia/Yerevan'),
    53: pytz.timezone('Asia/Kabul'),
    54: pytz.timezone('Asia/Yekaterinburg'),
    55: pytz.timezone('Asia/Karachi'),
    56: pytz.timezone('Asia/Kolkata'),
    57: pytz.timezone('Asia/Kolkata'),
    58: pytz.timezone('Asia/Kathmandu'),
    59: pytz.timezone('Asia/Novosibirsk'),
    60: pytz.timezone('Asia/Dhaka'),
    61: pytz.timezone('Asia/Rangoon'),
    62: pytz.timezone('Asia/Bangkok'),
    63: pytz.timezone('Asia/Krasnoyarsk'),
    64: pytz.timezone('Asia/Hong_Kong'),
    65: pytz.timezone('Asia/Singapore'),
    66: pytz.timezone('Asia/Irkutsk'),
    67: pytz.timezone('Australia/Perth'),
    68: pytz.timezone('Asia/Taipei'),
    69: pytz.timezone('Asia/Tokyo'),
    70: pytz.timezone('Asia/Seoul'),
    71: pytz.timezone('Asia/Yakutsk'),
    72: pytz.timezone('Australia/Adelaide'),
    73: pytz.timezone('Australia/Darwin'),
    74: pytz.timezone('Australia/Brisbane'),
    75: pytz.timezone('Australia/Sydney'),
    76: pytz.timezone('Australia/Hobart'),
    77: pytz.timezone('Pacific/Guam'),
    78: pytz.timezone('Asia/Vladivostok'),
    79: pytz.timezone('Asia/Magadan'),
    80: pytz.timezone('Pacific/Auckland'),
    81: pytz.timezone('Pacific/Fiji'),
    82: pytz.timezone('Pacific/Fakaofo'),
}


def tzid_from_dt(dt):
    if dt.tzinfo is None:
        return DEFAULT_TZ_ID
    for tzid, zone in pytz_zone.items():
        if zone.normalize(dt).utcoffset() == dt.utcoffset():
            # Same offset, let's pick this one.
            return tzid
    # No match found, return default
    return DEFAULT_TZ_ID


def get_timezone_info(timezone_id):
    timezone_id = int(timezone_id)
    timezone_pytz = pytz_zone[timezone_id]
    offset_time = timezone_pytz.utcoffset(datetime.now())
    offset_hours = offset_time.days * 24. + offset_time.seconds / 3600.
    return {'id': timezone_id,
            'offset': offset_hours,
            'daylight_saving': daylight_saving[timezone_id],
            'name': dict(timezone_list)['{0:0=2}'.format(timezone_id)],
            'zone': timezone_pytz.zone
            }


def get_pytz_timezone(timezone_id):
    # To stay compatible with old events during transition, we default to FRA
    if not timezone_id:
        timezone_id = DEFAULT_TZ_ID
    return pytz_zone[int(timezone_id)]


def escape_id_to_class(cid):
    """ We use workspace ids as classes to colour them.
        if a workspace has dots in its name, this is not usable as a class
        name. We have to escape that. Refs #10052
    """
    return (
        cid
        .replace('.', '-')
        .replace(':', '')
        .replace('+', '')
        .replace('(', '')
        .replace(')', '')
        .replace('&', '')
    )


def get_workspaces_of_current_user(context):
    """ Load workspaces from solr, no archived ones """
    user = api.user.get_current()
    if not user:
        return []
    key = "get_workspaces_of_current_user" + user.getId()
    cache = IAnnotations(context.REQUEST)
    data = cache.get(key, None)
    if data is None:
        query = dict(object_provides=IBaseWorkspaceFolder.__identifier__,
                     is_archived=False)

        sitesearch = getUtility(ISiteSearch)
        data = sitesearch.query(filters=query, step=99999)
        cache[key] = data

    # XXX we'll need to turn this into a dict to make it cacheable in memcached
    return data


def get_events_of_current_user(context):
    """ Load events from solr """
    # We only provide a history of 30 days, otherwise, fullcalendar has
    # too much to render. This could be made more flexible
    user = api.user.get_current()
    if not user:
        return []
    key = "get_events_of_current_user" + user.getId()
    cache = IAnnotations(context.REQUEST)
    data = cache.get(key, None)
    if data is None:
        evt_date = localized_now() - timedelta(30)
        query = dict(object_provides=IEvent.__identifier__,
                     end__gt=solr_date(evt_date))
        query['is_archived'] = False

        sitesearch = getUtility(ISiteSearch)
        data = sitesearch.query(filters=query, step=99999)
        cache[key] = data

    # XXX we'll need to turn this into a dict to make it cacheable in memcached
    return data


def get_calendars(context):

    # Get all the users workspaces
    # Get all the users events
    # sort the workspaces depending on events available and the users
    # rights within the workspaces and invitee status on the event

    my = defaultdict(list)
    invited = defaultdict(list)
    public = defaultdict(list)
    personal = defaultdict(list)
    other = defaultdict(list)

    user = api.user.get_current()
    groups = [
        x.getId() for x in api.group.get_groups(username=user.getId())
        if x is not None]

    groups.append(user.getId())

    all_workspaces = get_workspaces_of_current_user(context)
    w_by_path = {}
    for w in all_workspaces:
        ws_path = w.getPath()
        w_by_path[ws_path] = w

    all_events = get_events_of_current_user(context)
    event_by_cal = defaultdict(list)

    for e in all_events:
        ws_path = os.path.dirname(e.getPath())
        if ws_path not in w_by_path:
            # The immediate parent of this is event is not a workspace:
            # should not happen, we ignore it
            continue
        is_invited = (e.invitees and
                      set(groups).intersection(set(e.invitees)))

        if is_invited:
            invited[ws_path] = w_by_path[ws_path]
            event_by_cal['invited'].append(e)
        else:
            other[ws_path] = w_by_path[ws_path]
            event_by_cal['other'].append(e)

    return dict(
        events=event_by_cal,
        calendars={
            'my': my.values(),
            'invited': invited.values(),
            'public': public.values(),
            'personal': personal.values(),
            'other': other.values(),
        }
    )
