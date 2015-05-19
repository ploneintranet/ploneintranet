__author__ = 'benc'

from Products.Five import BrowserView
from plone import api


class CheckAuth(BrowserView):
    def __call__(self):
        if api.user.is_anonymous():
            print "User is anonymous"
            self.request.response.setStatus(403, lock=True)
        return 'OK'
