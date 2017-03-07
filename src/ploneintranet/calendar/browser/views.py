# coding=utf-8
from plone import api
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.memoize.view import memoize
from ploneintranet.calendar.config import TZ_COOKIE_NAME
from ploneintranet.workspace.interfaces import IBaseWorkspaceFolder
from Products.Five import BrowserView


class SetTimezoneView(BrowserView):

    def __call__(self):
        self.set_timezone_cookie(self.request.get('timezone'))
        return

    def set_timezone_cookie(self, tz):
        if tz:
            cookie_path = '/' + api.portal.get().absolute_url(1)
            self.request.response.setCookie(TZ_COOKIE_NAME, tz,
                                            path=cookie_path)


class CalendarMoreMenu(BrowserView):

    @property
    @memoize
    def target(self):
        ''' The target for the calendar export view
        '''
        for obj in self.context.aq_chain:
            if (
                IBaseWorkspaceFolder.providedBy(obj) or
                INavigationRoot.providedBy(obj)
            ):
                return obj
