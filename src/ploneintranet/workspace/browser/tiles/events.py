from plone import api
from plone.app.contenttypes.interfaces import IEvent
from plone.app.event.base import localized_now
from plone.tiles import Tile
from ploneintranet.core import ploneintranetCoreMessageFactory as _  # noqa
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


class EventsTile(Tile):

    def upcoming_events(self):
        """
        Return the events in this workspace
        to be shown in the events section of the sidebar
        """
        catalog = api.portal.get_tool('portal_catalog')
        now = localized_now()

        upcoming_events = catalog.searchResults(
            object_provides=IEvent.__identifier__,
            end={'query': now, 'range': 'min'},
            sort_on='start',
            sort_order='ascending',
        )
        return upcoming_events

    def format_event_date(self, event):
        """
        We need to show only the starting time, or in case of an all day event
        'All day' in the time tag. Not the date.

        In case of a multi day event, we can show "2015-08-30 - 2015-08-31"
        """
        # whole_day isn't a metadata field (yet)
        event_obj = event.getObject()
        if is_single_day(event) and event_obj.whole_day:
            return _(u'All day')
        elif is_single_day(event):
            return event.start.strftime('%H:%M')
        else:  # multi day event
            return '{} - {}'.format(
                event.start.strftime('%Y-%m-%d'),
                event.end.strftime('%Y-%m-%d'),
            )

    def month_name(self, date):
        """
        Return the full month name in the appropriate language
        """
        return month_name(self, date)
