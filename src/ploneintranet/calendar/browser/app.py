# coding=utf-8
# from datetime import date
# from DateTime import DateTime
# from plone.memoize import forever
# from plone.memoize.view import memoize
# from ploneintranet import api as pi_api
# from ploneintranet.core import ploneintranetCoreMessageFactory as _
# from ploneintranet.search.interfaces import ISiteSearch
# from zope.component import getUtility
# from zope.i18nmessageid.message import Message
# from calendar import FullCalendarMixin

from AccessControl.unauthorized import Unauthorized
from plone import api
from Products.Five import BrowserView

from plone.app.blocks.interfaces import IBlocksTransformEnabled

from ploneintranet.calendar.utils import escape_id_to_class
from ploneintranet.calendar.utils import get_calendars
from ploneintranet.layout.interfaces import IAppView

from zope.interface import implementer


@implementer(IBlocksTransformEnabled)
@implementer(IAppView)
class View(BrowserView):
    """ The (global) calendar app view """

    app_name = 'calendar'

    def update(self):
        if api.user.is_anonymous():
            raise Unauthorized
        # user = api.user.get_current()
        self.calendars = []  # XXX: UserData(user)['calendars']

    def get_workspaces_query_string(self):
        workspaces = self.request.get('workspaces', [])
        if workspaces:
            return '&{0}&all-cals:boolean={1}'.format('&'.join(
                ['workspaces:list={0}'.format(cal) for cal in workspaces]),
                self.request.get('all-cals', 'off') == 'on')
        return ''

    def get_calendars(self):
        return get_calendars(self.context)['calendars']

    def id2class(self, cal):
        return escape_id_to_class(cal)
