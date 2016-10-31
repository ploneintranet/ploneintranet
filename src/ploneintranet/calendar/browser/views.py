from Products.Five import BrowserView
from ploneintranet.calendar.config import TZ_COOKIE_NAME
from plone import api


class SetTimezoneView(BrowserView):

    def __call__(self):
        self.set_timezone_cookie(self.request.get('timezone'))
        return

    def set_timezone_cookie(self, tz):
        if tz:
            cookie_path = '/' + api.portal.get().absolute_url(1)
            self.request.response.setCookie(TZ_COOKIE_NAME, tz,
                                            path=cookie_path)
