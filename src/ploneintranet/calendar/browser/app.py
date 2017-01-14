# coding=utf-8
from collections import defaultdict
from datetime import timedelta
from logging import getLogger
from plone import api
from plone.app.blocks.interfaces import IBlocksTransformEnabled
from plone.app.contenttypes.interfaces import IEvent
from plone.app.event.base import localized_now
from plone.memoize.view import memoize_contextless
from ploneintranet.calendar.utils import escape_id_to_class
from ploneintranet.layout.interfaces import IAppView
from ploneintranet.layout.utils import get_record_from_registry
from ploneintranet.search.interfaces import ISiteSearch
from ploneintranet.workspace.interfaces import IBaseWorkspaceFolder
from Products.Five import BrowserView
from scorched.dates import solr_date
from zope.component import getUtility
from zope.interface import implementer

import os


logger = getLogger(__name__)


@implementer(IBlocksTransformEnabled)
@implementer(IAppView)
class View(BrowserView):
    """ The (global) calendar app view """

    app_name = 'calendar'
    _group_types = [
        'ploneintranet.userprofile.workgroup',
    ]

    def get_workspaces_query_string(self):
        workspaces = self.request.get('workspaces', [])
        if workspaces:
            return '&{0}&all-cals:boolean={1}'.format('&'.join(
                ['workspaces:list={0}'.format(cal) for cal in workspaces]),
                self.request.get('all-cals', 'off') == 'on')
        return ''

    @property
    @memoize_contextless
    def groups_container(self):
        ''' Returns the group container (if found) or an empty dictionary
        '''
        portal = api.portal.get()
        return portal.get('groups', {})

    @memoize_contextless
    def get_authenticated_groupids(self):
        ''' Look for user groups
        '''
        user = api.user.get_current()
        if not user:
            return []
        userid = user.getId()
        only_membrane_groups = get_record_from_registry(
            'ploneintranet.userprofile.only_membrane_groups',
            False,
        )
        if only_membrane_groups:
            mt = api.portal.get_tool('membrane_tool')
            groups = [
                b.getGroupId
                for b in mt.unrestrictedSearchResults(
                    workspace_members=userid,
                    portal_type=self._group_types,
                )
                if b.getGroupId
            ]
        else:
            groups = [
                x.getId() for x in api.group.get_groups(user=user)
                if x is not None
            ]
        groups.append(userid)
        return groups

    @memoize_contextless
    def get_authenticated_events(self):
        """ Load events from solr """
        # We only provide a history of 30 days, otherwise, fullcalendar has
        # too much to render. This could be made more flexible
        user = api.user.get_current()
        if not user:
            return []

        fullcalendar_day_span = api.portal.get_registry_record(
            'ploneintranet.calendar.fullcalendar_day_span',
            default=30,
        )
        evt_date = localized_now() - timedelta(fullcalendar_day_span)
        query = dict(
            object_provides=IEvent.__identifier__,
            end__gt=solr_date(evt_date)
        )
        query['is_archived'] = False

        sitesearch = getUtility(ISiteSearch)
        return sitesearch.query(filters=query, step=99999)

    @memoize_contextless
    def get_workspaces(self):
        ''' Look for user groups
        '''
        query = dict(
            object_provides=IBaseWorkspaceFolder.__identifier__,
            is_archived=False,
        )
        sitesearch = getUtility(ISiteSearch)
        data = sitesearch.query(filters=query, step=99999)
        return data

    def get_calendars(self):
        # Get all the users workspaces
        # Get all the users events
        # sort the workspaces depending on events available and the users
        # rights within the workspaces and invitee status on the event

        my = defaultdict(list)
        invited = defaultdict(list)
        public = defaultdict(list)
        personal = defaultdict(list)
        other = defaultdict(list)
        groups = set(self.get_authenticated_groupids())

        w_by_path = {
            w.getPath(): w for w in self.get_workspaces()
        }

        all_events = self.get_authenticated_events()

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
                invited[ws_path] = w_by_path[ws_path]
            elif is_public:
                public[ws_path] = w_by_path[ws_path]
            else:
                # Everything I can see
                my[ws_path] = w_by_path[ws_path]

        return {
            'my': my.values(),
            'invited': invited.values(),
            'public': public.values(),
            'personal': personal.values(),
            'other': other.values(),
        }

    def id2class(self, cal):
        return escape_id_to_class(cal)
