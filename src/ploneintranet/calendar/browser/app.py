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
from ploneintranet.calendar.utils import get_timezone_info
from ploneintranet.calendar.utils import pytz_zone
from ploneintranet.calendar.utils import get_calendars
from ploneintranet.layout.interfaces import IAppView

from zope.component import getUtility
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory


TZ_COOKIE_NAME = "ploneintranet.calendar.timezone"
timezone_number_by_name = {}
for k, v in pytz_zone.items():
    timezone_number_by_name[v.zone] = k


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

    def get_timezone_name_by_number(self, tz):
        return tz in timezone_number_by_name and \
            str(timezone_number_by_name[tz]) or '31'

    def get_timezone_cookie(self, context):
        return context.request.get(TZ_COOKIE_NAME, 'Europe/Berlin')

    def set_timezone_cookie(self, context, tz):
        if tz:
            cookie_path = '/' + api.portal.get().absolute_url(1)
            context.request.response.setCookie(TZ_COOKIE_NAME, tz,
                                               path=cookie_path)

    def get_calendars(self):
        return get_calendars(self.context)['calendars']

    def id2class(self, cal):
        return escape_id_to_class(cal)
