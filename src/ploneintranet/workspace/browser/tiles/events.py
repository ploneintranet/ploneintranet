from plone import api
from plone.app.contenttypes.interfaces import IEvent
from plone.app.event.base import localized_now
from plone.tiles import Tile
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.search.interfaces import ISearchResult
from ploneintranet.search.interfaces import ISiteSearch
from Products.ZCatalog.interfaces import ICatalogBrain
from scorched.dates import solr_date
from zope.component import getUtility
from zope.i18nmessageid import MessageFactory


pl_message = MessageFactory('plonelocales')


def format_event_date_for_title(event):
    """
    We need to show only the starting time, or in case of an all day event
    'All day' in the time tag. Not the date.

    In case of a multi day event, we can show "2015-08-30 - 2015-08-31"
    """
    # whole_day isn't a metadata field (yet)
    if ICatalogBrain.providedBy(event) or ISearchResult.providedBy(event):
        event_obj = event.getObject()
    else:
        event_obj = event
    start = event_obj.start
    end = event_obj.end
    if not (start and end) or (start.date() != end.date()):
        return '{} - {}'.format(
            start.strftime('%Y-%m-%d') if start else '',
            end.strftime('%Y-%m-%d') if end else '',
        )
    if event_obj.whole_day:
        return _(u'All day')
    return start.strftime('%H:%M')


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
        return [ev.getObject() for ev in upcoming_events]

    def format_event_date(self, event):
        return format_event_date_for_title(event)
