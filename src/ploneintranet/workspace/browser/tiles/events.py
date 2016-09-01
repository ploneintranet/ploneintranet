from plone import api
from plone.app.contenttypes.interfaces import IEvent
from plone.app.event.base import localized_now
from plone.tiles import Tile
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.search.interfaces import ISiteSearch
from scorched.dates import solr_date
from zope.component import getUtility
from zope.i18nmessageid import MessageFactory
from ploneintranet.workspace.utils import month_name


pl_message = MessageFactory('plonelocales')


def is_single_day(event):
    start = event.start
    end = event.end
    if not end:
        return True
    elif start.day == end.day and (end - start).days < 1:
        return True
    else:
        return False


def format_event_date_for_title(event):
    """
    We need to show only the starting time, or in case of an all day event
    'All day' in the time tag. Not the date.

    In case of a multi day event, we can show "2015-08-30 - 2015-08-31"
    """
    # whole_day isn't a metadata field (yet)
    event_obj = event.getObject()
    if is_single_day(event_obj) and event_obj.whole_day:
        return _(u'All day')
    elif is_single_day(event_obj):
        return event_obj.start.strftime('%H:%M')
    else:  # multi day event
        return '{} - {}'.format(
            event_obj.start.strftime('%Y-%m-%d'),
            event_obj.end.strftime('%Y-%m-%d'),
        )


class EventsTile(Tile):

    def upcoming_events(self):
        """
        Return upcoming events, potentially filtered by invitation status
        and/or search term
        """
        now = localized_now()

        query = dict(
            object_provides=IEvent.__identifier__,
            end__gt=solr_date(now),
        )
        phrase = None
        if self.data.get('SearchableText', ''):
            phrase = self.data['SearchableText'] + '*'
        elif self.data.get('my_events', True):
            query['invitees'] = [api.user.get_current().getId()]

        search_util = getUtility(ISiteSearch)
        upcoming_events = search_util.query(
            phrase=phrase,
            filters=query,
            sort='start',
        )
        return upcoming_events

    def format_event_date(self, event):
        return format_event_date_for_title(event)

    def month_name(self, date):
        """
        Return the full month name in the appropriate language
        """
        return month_name(self, date)
