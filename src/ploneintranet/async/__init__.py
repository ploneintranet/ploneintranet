__author__ = 'benc'

from Products.Five import BrowserView
from ploneintranet.async.celerytasks import message
from plone import api


class CheckAuth(BrowserView):
    def __call__(self):
        if api.user.is_anonymous():
            print "User is anonymous"
            self.request.response.setStatus(403, lock=True)
        return api.user.get_current().id


class SendMessage(BrowserView):
    def __call__(self):
        if api.user.is_anonymous():
            print "User is anonymous"
            self.request.response.setStatus(403, lock=True)
        # message.delay(api.user.get_current().id, "Here is a message")
        # Hardcode for admin for now.
        message.delay('admin', u'Here is a message for admin.')
        return 'Message scheduled'
