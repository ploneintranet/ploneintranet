from plone import api
from plone.app.contenttypes.interfaces import IEvent
from plone.app.event.base import localized_now
from plone.tiles import Tile


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
        )
        return upcoming_events
